from client import *
from image import *
import optparse, os

def option_parser(usage=None):
    parser = optparse.OptionParser(usage)
    parser.add_option("-U", "--username", dest="user", default=os.environ.get("OAM_USERNAME"), help="OAM username")
    parser.add_option("-P", "--password", dest="passwd", default=os.environ.get("OAM_PASSWORD"), help="OAM password")
    parser.add_option("-S", "--service", dest="service", help="OAM service base URL", default=default_service)
    parser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False, help="verbose mode (dump HTTP errors)")
    parser.add_option("-t", "--test", dest="test", action="store_true", default=False, help="Test mode (don't post to server)")
    return parser

def parse_bbox(args):
    bbox = map(float, args)
    if len(bbox) != 4 or bbox[0] >= bbox[2] or bbox[1] >= bbox[3]:
        raise Exception("You must provide a proper bounding box!")
    return bbox

def build_client(opts):
    return Client(opts.user, opts.passwd, opts.service, opts.verbose, opts.test)
