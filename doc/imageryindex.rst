Imagery Index
=============

The imagery index is the core of the OpenAerialMap project. It acts as a
clearinghouse for the OpenAerialMap imagery data.

The core object in the imagery index is an :ref:`image`. There are two types
of images -- an Archive image, and a Processed image. 
 
* Archive Image: This is designed to be metadata about a file which
  has not been processed for OAM, but which could be processed either by
  tools or by a human. This might mean that the imagery is only available
  in a compressed format, or is in an unusual projection. Generally 
  speaking, this is the case for imagery provided over the web by
  most government agencies.

* Processed Image: A processed image is an image which has been specifically
  created for OAM, or fits the needs of an OAM client well. For more details,
  see :ref:`optimized`.

The default for images which are uploaded to OpenAerialMap is to be archive
images. To change this, set the archive flag of the image to False when 
uploading.

General API Information
+++++++++++++++++++++++

The Imagery Index API is designed with REST in mind. At its core, each 
resource has a representation as JSON.  

Authentication
--------------

Requests to write to the database require authenticated requests. 
Authentication is handled via basic auth; you must register for an
account via the web interface first. 

Once you have registered, simply use Basic Auth with your requests 
to authenticate. If you do not send basic auth headers, you will 
receive a 401 response.

Errors
------

Errors are represented in JSON. They will have an 'error' key, and a 'type'
key. They also have an 'unexpected' key, which indicates whether the 
error is something that application was expecting; in cases where the 
server is broken in some way, you will get an 'unexpected' key set to
true instead of false.

::

  {
    "unexpected": false, 
    "type": "ApplicationError", 
    "error": "No width provided for image., No height provided for image., No BBOX provided for image., No license ID was passed"
  }

.. _image:

License API
+++++++++++

API Path: /api/license/

Simplest License POST::
 
 {
   "name": "Public Domain",
 }

Response::

  {
    "id": 1, 
    "url": "", 
    "additional": "", 
    "options": {
        "attribution": false, 
        "sharealike": false, 
        "noncommercial": false
    }, 
    "name": "Public Domain"
  }

The 'options' object can contain boolean flags for:

* 'noncommercial'
* 'attribution'
* 'sharealike'

Each option is a boolean option to control whether the flag applies to the 
license in question.

For example, for the CC-By-NC-SA license, you would post something like::

 { 
    "name": "CC-BY-NC-SA",
    "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/",
    "options": { 
        "noncommercial": true, 
        "sharealike": true, 
        "attribution": true 
    }
  } 

Note that once a license is created, it is possible to use the license
by simply referring to it by the ID returned in the POST response.

::

 { 
    "id": 5,
    "name": "CC-BY-NC-SA",
    "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/",
    "options": { 
        "noncommercial": true, 
        "sharealike": true, 
        "attribution": true 
    }
  }

The following licenses are available are provided as part of the index.

* **1**: `Public Domain <http://creativecommons.org/publicdomain/zero/1.0/>`_ 
* **2**: `CC-By <http://creativecommons.org/licenses/by/3.0/>`_
* **3**: `CC-By-SA <http://creativecommons.org/licenses/by-sa/3.0/>`_
* **4**: `CC-By-NC <http://creativecommons.org/licenses/by-nc/3.0/>`_
* **5**: `CC-By-NC-SA <http://creativecommons.org/licenses/by-nc-sa/3.0/>`_
 
Image API
+++++++++

API Path: /api/image/

Simplest Image POST::

  {
      "url": "http://example.com/200.tif", 
      "width": 200, 
      "height": 200, 
      "bbox": [-180,-90,180,90], 
      "license": 1
  }

POSTing this to http://catalog.example.com/api/image/ will return a simple 
representation::

  { 
    "hash": null,
    "vrt": null,
    "height": 200,
    "bbox": [-180.0, -90.0, 180.0, 90.0],
    "file_size": null,
    "id": 1,
    "crs": null,
    "archive": true,
    "license": {
      "url":  "",
      "flags": {},
      "name":  "Public Domain",
      "additional":  "",
      "id": 1
    },
    "file_format": null,
    "source_url": "http://example.com/200.tif",
    "urls": ["http://example.com/200.tif", "http://example.com/400.tif"],
    "vrt_date": null,
    "width": 200
  }

The "archive" flag will be set to True by default. If the image you are
uploading has been processed, then you should set this property to false,
to indicate that it is a processed image. See :ref:`optimized` for more 
information on processed images.

Note that the OAM server will 'crawl'/spider processed images, confirming
that they meet the specification outlined in the linked document. If your
image is marked processed, but the image is not in the format specified,
the image will be reverted to an 'archive' image, and a warning will be 
recorded in the database.

Server
++++++

Currently, an implementation of the OAM Imagery Index is available and running
at:

  http://oam.osgeo.org/
