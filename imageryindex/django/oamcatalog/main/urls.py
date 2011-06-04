from django.conf.urls.defaults import *

urlpatterns = patterns('main.views',
    # Example:
    (r'^$', 'home'),
    (r'^image/(?P<id>[0-9]+)/$', 'image_browse'),
    (r'^layer/(?P<id>[0-9]+)/', 'layer_browse'),
    (r'^license/(?P<id>[0-9]+)/$', 'license_browse'),
    (r'^api/layer/$', 'layer'),
    (r'^api/layer/(?P<id>[0-9]+)/$', 'layer'),
    (r'^api/license/$', 'license'),
    (r'^api/license/(?P<id>[0-9]+)/$', 'license'),
    (r'^api/image/$', 'image'),
    (r'^api/image/(?P<id>[0-9]+)/$', 'image'),
    (r'^api/mirror/$', 'mirror'),
    (r'^api/mirror/(?P<id>[0-9]+)/$', 'mirror'),
)
