Frequently Asked Questions
==========================

Why not WMS?
------------

For many tasks, WMS is the right solution: it is a relatively widely used
standard, and one that is easy to create and consume. However, because WMS
was primarily designed for use by clients to download a small area of a
map, it is not ideal for many of the use cases that are needed by OAM.

* Use offline -- One of the canonical use cases for OAM-style imagery is 
  for use in disaster situations. In those situations, access to an 'online'
  API is inappropriate due to poor internet connectivity, and downloading
  data is neccesary. WMS does not make this possible.

* Access to larger areas -- In general, WMS services limit request sizes 
  to smaller than a certain area. This limit can be impractical for users
  who need to produce images for reports or other similar offline use.

* Mosaicing -- In general, when delivering output data as JPEG, mosaicing
  responses from multiple services together is hard or impossible.

* Access Time -- In general, WMS access is optimized for typical WMS clients,
  which request a single larger image. For these types of clients, WMS
  is 'fast enough' -- taking a second or more to render a scene is not
  a problem. However, many of the use cases behind OAM are the types of
  use cases that require much more interactivity, and using a slow WMS
  like this is untenable for the number of clients who might view an area.

  The primary purpose for not making OAM host imagery products/access tools
  itself is to help eliminate bottlenecks in mission-critical services by
  allowing them to be replicated in the places they're needed most.
 

Why not GeoNetwork?
-------------------

GeoNetwork Open Source is a catalog designed to catalog services. For this
task, it is reasonably ideally suited, but OAM is explicitly taking a 
different path, and seeking to index data at the image level.

Although there are some similarities in the cataloging task, overall, it
seemed as if GeoNetwork was not ideally suited to serve as the backend
for the Imagery Index of OAM.
