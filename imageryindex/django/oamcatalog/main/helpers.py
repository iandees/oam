from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse
import django.conf
import sys
import traceback
import simplejson
import base64

from django.http import HttpResponse
from django.contrib.auth import authenticate, login

class ApplicationError(Exception):
    errors = None
    status_code = 200
    def __init__(self, errors):
        self.errors = errors
    def __str__(self):
        return ", ".join(self.errors)

def text_error_response(error):
    response = []
    response.append("Error Type: %s\n" %  error['type'])
    if error['unexpected']:
        response.append("An unexpected error occurred!\n")

    response.append("Error: %s\n" %  error['error'])
    if error.has_key('traceback'):
        response.append("Traceback:\n\n%s" %  error['traceback'])
    
    
    r = HttpResponse(response)
    r['Content-Type'] = "text/plain"
    return r

def generate_error_response(exception, format="text", status_code=None, request=None, unexpected=False):
    """Generate an error response, used in textexception/jsonexception
       decorators.
       
       >>> try:
       ...     int('a')
       ... except Exception, E:
       ...    response = generate_error_response(E) 
       >>> response.status_code 
       500
       >>> response.content.find("Error Type: ValueError")
       0
       
       >>> try:
       ...     raise ApplicationError("Failed")
       ... except ApplicationError, E:
       ...    response = generate_error_response(E) 
       >>> response.status_code
       200
       >>> "Error: Failed" in response.content
       True

       >>> try:
       ...     raise ApplicationError("Failed")
       ... except ApplicationError, E:
       ...    h = HttpRequest()
       ...    response = generate_error_response(E, format='json', request=h)
       >>> data = simplejson.loads(response.content)
       >>> data['error']
       u'Failed'
       
    """ 
     
    type = sys.exc_type.__name__
    error = {'error': str(exception), 'type': type, 'unexpected':unexpected}
    if django.conf.settings.DEBUG and unexpected:
        error['traceback'] = traceback.format_exc()
    
    if format == "json" and request:
        response = json_response(request, error)
    else:
        response = text_error_response(error)
    
    if hasattr(exception, "status_code"):
        response.status_code = exception.status_code
    elif status_code:
        response.status_code = status_code
    else:
        response.status_code = 500
    
    return response
    

def textexception(func):
    def wrap(request, *args, **kw):
        try:
            return func(request, *args, **kw)
        
        except ObjectDoesNotExist, E:
            return generate_error_response(E, status_code=404)
        
        except Http404, E:
            return generate_error_response(E, status_code=404)
        
        except ApplicationError, E:
            return generate_error_response(E)
            
        except Exception, E:
            return generate_error_response(E, unexpected=True)
    
    return wrap        

def jsonexception(func):
    def wrap(request, *args, **kw):
        try:
            return func(request, *args, **kw)
        
        except ObjectDoesNotExist, E:
            return generate_error_response(E, format="json", request=request, status_code=404)
        
        except Http404, E:
            return generate_error_response(E, format="json", request=request, status_code=404)
        
        except ApplicationError, E:
            return generate_error_response(E, format="json", request=request)
            
        except Exception, E:
            return generate_error_response(E, format="json", request=request, unexpected=True)
    return wrap        

def json_response(request, obj):
    """Take an object. If the object has a to_json method, call it, 
       and take either the result or the original object and serialize
       it using simplejson. If a callbakc was sent with the http_request,
       wrap the response up in that and return it, otherwise, just return
       it."""
    if hasattr(obj, 'to_json'):
        obj = obj.to_json()
    if request.GET.has_key('_sqldebug'):
        import django.db
        obj['sql'] = django.db.connection.queries
    data = simplejson.dumps(obj)
    if request.GET.has_key('callback'):
        data = "%s(%s);" % (request.GET['callback'], data)
    elif request.GET.has_key('handler'):
        data = "%s(%s);" % (request.GET['handler'], data)
    
    r = HttpResponse(data)
    r['Access-Control-Allow-Origin'] = "*"
    return r

def view_or_basicauth(view, request, test_func, realm = "", *args, **kwargs):
    """
    This is a helper function used by both 'logged_in_or_basicauth' and
    'has_perm_or_basicauth' that does the nitty of determining if they
    are already logged in or if they have provided proper http-authorization
    and returning the view if all goes well, otherwise responding with a 401.
    """
    if test_func(request.user):
        # Already logged in, just return the view.
        #
        return view(request, *args, **kwargs)

    # They are not logged in. See if they provided login credentials
    #
    uname = None
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: We are only support basic authentication for now.
            #
            if auth[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth[1]).split(':')
                user = authenticate(username=uname, password=passwd)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        request.user = user
                        return view(request, *args, **kwargs)

    # Either they did not provide an authorization header or
    # something in the authorization attempt failed. Send a 401
    # back to them to ask them to authenticate.
    #
    message = "You must be authenticated to use this service.\n"
    if uname:
        message = "You must be authenticated to use this service. (Authentication failed for %s.)\n" % uname
    response = HttpResponse(message)
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="%s"' % realm
    return response
    
#############################################################################
#
def logged_in_or_basicauth(realm = ""):
    """
    A simple decorator that requires a user to be logged in. If they are not
    logged in the request is examined for a 'authorization' header.

    If the header is present it is tested for basic authentication and
    the user is logged in with the provided credentials.

    If the header is not present a http 401 is sent back to the
    requestor to provide credentials.

    The purpose of this is that in several django projects I have needed
    several specific views that need to support basic authentication, yet the
    web site as a whole used django's provided authentication.

    The uses for this are for urls that are access programmatically such as
    by rss feed readers, yet the view requires a user to be logged in. Many rss
    readers support supplying the authentication credentials via http basic
    auth (and they do NOT support a redirect to a form where they post a
    username/password.)

    Use is simple:

    @logged_in_or_basicauth
    def your_view:
        ...

    You can provide the name of the realm to ask for authentication within.
    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.is_authenticated(),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator

#############################################################################
#
def has_perm_or_basicauth(perm, realm = ""):
    """
    This is similar to the above decorator 'logged_in_or_basicauth'
    except that it requires the logged in user to have a specific
    permission.

    Use:

    @logged_in_or_basicauth('asforums.view_forumcollection')
    def your_view:
        ...

    """
    def view_decorator(func):
        def wrapper(request, *args, **kwargs):
            return view_or_basicauth(func, request,
                                     lambda u: u.has_perm(perm),
                                     realm, *args, **kwargs)
        return wrapper
    return view_decorator


