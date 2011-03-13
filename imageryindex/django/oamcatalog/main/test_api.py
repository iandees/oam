POST /api/license/
"""
{
  "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/", 
  "additional": "", 
  "options": {
    "attribution": true, 
    "sharealike": true, 
    "noncommercial": true
  }, 
  "name": "CC-BY-NC-SA"
}
"""
"""
{
  "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/", 
  "additional": "", 
  "options": {
    "attribution": true, 
    "sharealike": true, 
    "noncommercial": true
  }, 
  "id": 1, 
  "name": "CC-BY-NC-SA"
}
"""
POST /api/license/
"""
{
  "warnings": [
    "URL of license matched existing license 1; updating that license instead of creating a new license."
  ], 
  "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/", 
  "additional": "", 
  "options": {
    "attribution": true, 
    "sharealike": true, 
    "noncommercial": true
  }, 
  "id": 1, 
  "name": "CC-BY-NC-SA"
}
"""
GET /api/license/
"""
{
  "licenses": [
    {
      "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/", 
      "additional": "", 
      "options": {
        "attribution": true, 
        "sharealike": true, 
        "noncommercial": true
      }, 
      "id": 1, 
      "name": "CC-BY-NC-SA"
    }
  ]
}
"""
GET /api/image/
"""
{
  "images": [
  ]
}
"""
POST /api/image/
"""
{
    "url": "http://example.com/test.tif",
    "width": 512,
    "height": 512,
    "license": 1,
    "bbox": [-180,-90,180,90]
}
"""
"""
{
  "unexpected": false, 
  "type": "ApplicationError", 
  "error": "Attribution is required when using CC-BY-NC-SA (ID: 1)"
}
"""
POST /api/image/
"""
{
    "url": "http://example.com/test.tif",
    "width": 512,
    "height": 512,
    "license": 1,
    "bbox": [-180,-90,180,90],
    "attribution": "Nobody"
}
"""
"""{
  "hash": null, 
  "vrt": null, 
  "height": 512,
  "attribution": "Nobody", 
  "bbox": [
    -180.0, 
    -90.0, 
    180.0, 
    90.0
  ], 
  "file_size": null, 
  "vrt_date": null, 
  "archive": true, 
  "crs": null, 
  "license": {
    "url": "http://creativecommons.org/licenses/by-nc-sa/3.0/", 
    "additional": "", 
    "options": {
      "attribution": true, 
      "sharealike": true, 
      "noncommercial": true
    }, 
    "id": 1, 
    "name": "CC-BY-NC-SA"
  }, 
  "file_format": null, 
  "url": "http://example.com/test.tif", 
  "id": 1, 
  "width": 512, 
  "user": 1
}
"""
POST /api/image/
"""
{
    "url": "http://example.com/test.tif",
    "width": 512,
    "height": 512,
}
"""
"""
{
  "unexpected": false, 
  "type": "ApplicationError", 
  "error": "No BBOX provided for image., No license ID was passed"
}
"""
POST /api/image/
"""
{
    "url": "http://example.com/test.tif",
    "width": 512,
    "height": 512,
    "license": {
        "url": "http://creativecommons.org/choose/zero/"
    },
    "bbox": [-180,-90,180,90]
}
"""
"""
{
  "hash": null, 
  "vrt": null, 
  "height": 512, 
  "bbox": [
    -180.0, 
    -90.0, 
    180.0, 
    90.0
  ], 
  "file_size": null, 
  "vrt_date": null, 
  "archive": true, 
  "crs": null, 
  "license": {
    "url": "http://creativecommons.org/choose/zero/", 
    "additional": "", 
    "options": {
      "attribution": false, 
      "sharealike": false, 
      "noncommercial": false
    }, 
    "id": 3, 
    "name": ""
  }, 
  "file_format": null, 
  "url": "http://example.com/test.tif", 
  "id": 6, 
  "width": 512, 
  "user": 1
}
"""
GET /api/mirror/
"""
{
  "mirrors": []
}
"""
POST /api/mirror/
"""
{"image": 2, "url": "http://google.com/foo/"}
"""
"""
{
  "url": "http://google.com/foo/", 
  "image": 2, 
  "user": 1
}
"""
GET /api/mirror/?image=2
"""
{
  "mirrors": [
    {
      "url": "http://google.com/foo/", 
      "image": 2, 
      "user": 1
    }
  ]
} 
"""
