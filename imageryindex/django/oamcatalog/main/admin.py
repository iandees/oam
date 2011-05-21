from django.contrib.gis import admin
from models import License, Attribution, Layer, Image, Mirror, WMS

admin.site.register(License)
admin.site.register(Attribution)
admin.site.register(Layer)
admin.site.register(Image)
admin.site.register(Mirror)
admin.site.register(WMS)
