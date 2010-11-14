from image import Image
import sys, urllib, urllib2, base64
try:
    import json
    json
except ImportError:
    import simplejson as json

default_service = 'http://oam.osgeo.org/api/'

class ClientException(Exception):
    pass

class Client(object):
    def __init__(self, user, password, service=default_service, verbose=False, test=False, **kwargs):
        """ Client for OAM index.
        
            Arguments:
            
              user:
                Username for index basic auth, assigned to self.user but currently unused.
              
              password:
                Password for index basic auth, assigned to self.password but currently unused.
              
              service:
                Base URL of OAM index, assigned to self.service, defaults to http://oam.osgeo.org/api/.
              
              verbose:
                Boolean flag for chattiness, assigned to self.verbose.
              
              test:
                Boolean flag for testiness, assigned to self.test.
        """
        self.user = user
        self.password = password
        self.service = service
        self.verbose = verbose
        self.test = test
        if not self.service.endswith("/"):
            self.service += "/"
        #passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        #passwd_mgr.add_password(None, self.service, user, password)
        #handler = urllib2.HTTPBasicAuthHandler(passwd_mgr)
        #self.http = urllib2.build_opener(handler)
        self.http = urllib2.build_opener()

    def notify(self, msg, *args):
        if self.verbose:
            print >>sys.stderr, msg % args,

    def debug(self, msg, *args):
        if self.verbose:
            self.notify(msg + "\n", *args)

    def request(self, method, endpoint, args=""):
        url = self.service + endpoint
        if method == "POST":
            # we presume args is a JSON object
            args = json.dumps(args)
            req = urllib2.Request(url, args)
        else:
            # we presume args is a dict, if anything
            if args:
                args = urllib.urlencode(args)
                url += "?" + args
            req = urllib2.Request(url)
        self.notify("%s %s", method, url)

        base64string = base64.encodestring(
                '%s:%s' % (self.user, self.password))[:-1]
        authheader =  "Basic %s" % base64string
        req.add_header("Authorization", authheader)

        if self.test:
            self.debug("%s", args)
            return None
        try:
            response = self.http.open(req)
        except IOError, e:
            if self.verbose and hasattr(e, "read"): # avoid calling e.read()
                self.debug("error: %s", e.read())
            raise
        result = response.read()
        data = json.loads(result)
        if "error" in result:
            raise ClientException(result["error"])
        self.debug("OK") 
        return data

    def layer(self, layer_id, **args):
        return self.request("GET", "layer/%s" % layer_id, args)

    def image(self, image_id, **args):
        endpoint = "image/%d" % image_id
        result = self.request("GET", endpoint, args)
        if self.test and not result: return None
        # JSON dict keys are unicode, which can't be used as function keyword args
        opts = dict((str(key), val) for key, val in result.items())
        return Image(**opts)

    def images_by_bbox(self, bbox, **args):
        args["bbox"] = "%f,%f,%f,%f" % tuple(bbox)
        result = self.request("GET", "image/", args)
        if self.test and not result: return None
        images = []
        for object in result["images"]:
            # JSON dict keys are unicode, which can't be used as function keyword args
            opts = dict((str(key), val) for key, val in object.items())
            image = Image(**opts)
            images.append(image)
        return images

    def save_image(self, image):
        return self.request("POST", "image/", image.to_dict())
