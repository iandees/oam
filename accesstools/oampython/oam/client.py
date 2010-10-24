import sys, os, urllib, urllib2
try:
    import json
    json
except ImportError:
    import simplejson as json

default_service = 'http://oam.osgeo.org/api/'

class Client(object):
    def __init__(self, user, password, service=default_service, verbose=False, test=False, **kwargs):
        self.user = user
        self.password = password
        self.service = service
        self.verbose = verbose
        self.test = test
        if not self.service.endswith("/"):
            self.service += "/"
        passwd_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        passwd_mgr.add_password(None, self.service, user, password)
        handler = urllib2.HTTPBasicAuthHandler(passwd_mgr)
        self.http_client = urllib2.build_opener(handler)

    def notify(self, msg, *args):
        if self.verbose:
            print >>sys.stderr, msg % args,

    def debug(self, msg, *args):
        if self.verbose:
            self.notify(msg + "\n", args)

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
        if self.test:
            self.debug(args)
            return None
        try:
            response = self.http_client.open(req)
        except IOError, e:
            if self.verbose: # avoid calling e.read()
                self.debug("error: %s", e.read())
            raise
        result = response.read()
        data = json.loads(result)
        if "error" in result:
            raise Exception(result["error"])
        self.debug("OK") 
        return data

    def layer(self, layer_id, **args):
        return self.request("GET", "layer/%s" % layer_id, args)

    def image(self, image_id, **args):
        endpoint = "image/%d" % image_id
        result = self.request("GET", endpoint, args)
        if self.test and not result: return None
        return Image(**result)

    def images_by_bbox(self, bbox, **args):
        endpoint = "image/?bbox=%f,%f,%f,%f" % tuple(opts.bbox)
        result = self.request("GET", endpoint, args)
        if self.test and not result: return None
        images = []
        for obj in result["images"]:
            image = Image(**obj)
            images.append(image)
        return images

    def save_image(self, image):
        return self.request("POST", "image/", content)
