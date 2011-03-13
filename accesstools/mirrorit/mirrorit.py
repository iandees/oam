import sys
import os
import optparse
import json
import urllib

def run(image, base_url, local_path):
    u = urllib.urlopen("http://oam.osgeo.org/api/image/%s/" % image)  
    data = json.load(u)
    url = data['source_url']
    def hook(x,y,z):
        prog = "Grabbing image %s: %.2f%% done" % (image, min((float(x)/(z/y)), 1) * 100)
        sys.stdout.write("\r%s\r" % (prog))
        sys.stdout.flush()
    last_part = url.split("/")[-1]
    path = os.path.join(local_path, last_part)
    urllib.urlretrieve(url, path, hook)
    print


if __name__ == "__main__":
    parser = optparse.OptionParser()
    parser.add_option("-i", "--image", dest="image", 
        help="ID of the image you wish to mirror")
    parser.add_option("-b", "--base", dest="base_url", help="Base URL you wish to add to")
    parser.add_option("-p", "--path", dest="local_path", default=".", help="local path to write mirror to. Should end in /.")
    (options, args) = parser.parse_args()
    run(options.image, options.base_url, options.local_path)
