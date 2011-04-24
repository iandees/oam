# OpenAerialMap

OpenAerialMap is a community project aiming to steward open aerial imagery.

The core of OpenAerialMap is django-powered index server hosted at: http://oam.osgeo.org/.

Documentation can be found at: http://oam.github.com/

This repository contains a variety of the software tools coming together to make OAM a reality.


# Installation

OAM needs at least GDAL 1.8.0 that includes the [VSI Curl feature](http://crschmidt.net/blog/archives/425/vsi-curl-support/). So, we install from source:

    wget http://download.osgeo.org/gdal/gdal-1.8.0.tar.gz
    tar xvf gdal-1.8.0.tar.gz
    cd gdal-1.8.0
    ./configure --with-libtiff=/usr/lib --with-curl=/usr/bin/curl-config

Note: the `--with-libtiff` is important to ensure libgdal links against the system version of libtiff instead of its internal version. If other software is installed (like mapnik) that links to the system version of libtiff, GDAL must also link to the same libtiff when used in the running process.

Also, if you run into problems with gdal try setting `export CPL_DEBUG=True` which will cause debugging info to be dumped out.