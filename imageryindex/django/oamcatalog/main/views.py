# Create your views here.
from django.http import HttpResponse
from main.models import Layer, Image, User, License, Mirror
from django.contrib.gis.geos import Polygon
from main.helpers import *
from django.shortcuts import render_to_response, get_object_or_404

try:
    import json
except ImportError:
    import simplejson as json

@jsonexception
def layer(request, id=None):
    @logged_in_or_basicauth()
    def handle_update(request, layer):
        data = json.loads(request.raw_post_data)
        warnings = []
        layer.from_json(data, request.user)
        layer.save()
        return json_response(request, layer)
    if id == None and request.method == "POST":
        l = Layer()
        return handle_update(request, l)
    elif id != None and request.method == "POST":
        l = Layer.objects.get(pk=id)
        return handle_update(request, l)
    else:
        layers = Layer.objects.all()
        data = {'layers': [
            l.to_json() for l in layers
            ]
        }    
        return json_response(request, data)

@jsonexception
def license(request, id=None):
    @logged_in_or_basicauth()
    def handle_update(request, license):
        data = json.loads(request.raw_post_data)
        warnings = []
        if not license.id:
            if 'url' in data:
                ls = License.objects.filter(url=data['url'])
                if ls.count():
                    license = ls[0]
                    warnings.append("URL of license matched existing license %s; updating that license instead of creating a new license." % ls[0].id) 
        license.from_json(data)
        license.save()
        return json_response(request, license, warnings=warnings)
    if id == None and request.method == "POST":
        l = License()
        return handle_update(request, l)
    elif id != None:
        l = License.objects.get(pk=id)
        if request.method == "DELETE":
            l.delete()
            return json_response(request, "")
        if request.method == "POST":
            return handle_update(request, l)
        return json_response(request, l)
    else:
        licenses = License.objects.all()
        data = {'licenses': [
            l.to_json() for l in licenses 
            ]
        }   
        return json_response(request, data)

@jsonexception
def mirror(request, id=None):
    @logged_in_or_basicauth()
    def handle_update(request, mirror):
        data = json.loads(request.raw_post_data)
        mirror.from_json(data, request.user)
        mirror.save()
        return json_response(request, mirror)
    if id == None and request.method == "POST":
        m = Mirror()
        return handle_update(request, m)
    elif id != None:
        m = Mirror.objects.get(pk=id)
        if request.method == "DELETE":
            m.delete()
            return json_response(request, "")
        elif request.method == "POST":
            return handle_update(request, m)
        return json_response(request, m)
    else:
        mirrors = Mirror.objects.all()
        if 'image' in request.GET:
            mirrors = mirrors.filter(image__id=request.GET['image'])
        data = {'mirrors': [mirror.to_json() for mirror in mirrors]}   
        return json_response(request, data) 

@jsonexception
def image(request, id=None):
    @logged_in_or_basicauth()
    def handle_update(request, image):
        data = json.loads(request.raw_post_data)
        image.from_json(data, request.user)
        image.save()
        return json_response(request, image)
        
    if id == None and request.method == "POST":
        i = Image()
        return handle_update(request,i)
    elif id != None:
        i = Image.objects.get(pk=id)
        if request.method == "DELETE":
            i.delete()
            return json_response(request, "")
        elif request.method == "POST":
            return handle_update(request, i)
        return json_response(request, i)
    else:
        images = Image.objects.all().select_related()
        output = request.GET.get('output', 'simple')
        if 'archive' in request.GET and request.GET['archive'].lower() in ("true", "t", "1"):
            images = images.filter(archive=True)
        else:
            images = images.filter(archive=False)
        if 'layer' in request.GET:
            images = images.filter(layers__id=request.GET['layer'])
        if 'bbox' in request.GET:
            left, bottom, right, top = map(float, request.GET['bbox'].split(","))
            box = Polygon.from_bbox([left, bottom, right, top])
            images = images.filter(bbox__intersects=box)
        limit = int(request.GET.get("limit", 10000))   
        if limit > 10000:
            limit = 10000
        start = int(request.GET.get("start", 0))    
        end = start + limit
        images = images.order_by("-id")    
        data = {'images': [
            i.to_json(output=output) for i in images[start:end]
            ]
        }   
        return json_response(request, data)

def home(request):
    images = Image.objects.order_by("-id")[0:10]
    return render_to_response("home.html", {'images': images})

def license_browse(request, id):
    l = License.objects.get(pk=id)
    images = l.image_set.order_by("-id")[0:5]
    return render_to_response("license.html", {'license': l, 'recent_images': images})

def layer_browse(request, id):
    l = get_object_or_404(Layer, pk=id)
    return render_to_response("layer.html", {'layer': l})
def image_browse(request, id):
    i = Image.objects.get(pk=id)
    return render_to_response("image.html", {'image': i})
