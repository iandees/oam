""" In-progress TileStache provider for OpenAerialMap.

TODO:
    - stop using hard-coded junk username/password in oam.Client constructor.
    - add archive server blacklist and whitelist.
    - enforce spherical mercator projection?
    - allow for local cache of big remote files

Example configuration file:

    {
      "cache": { "name": "Test" },
      "layers": 
      {
        "oam":
        {
            "provider": {"class": "oam.tiles.Provider"}
        }
      }
    }

Read more about TileStache and its configuration here:
    http://tilestache.org/doc/
    http://tilestache.org/doc/#configuring-tilestache
"""
from tempfile import mkstemp
from os import close, unlink
from urlparse import urljoin
from copy import deepcopy
from xml.dom.minidom import getDOMImplementation

import oam
import PIL.Image

from ModestMaps.Core import Point
from TileStache.Core import KnownUnknown

try:
    from osgeo import gdal
    from osgeo import osr
except ImportError:
    # well it won't work but we can still make the documentation.
    pass

class Provider:
    
    def __init__(self, layer):
        self.layer = layer
        self.client = oam.Client('username', 'password')

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
    
        garbage = []
        
        try:
            # Figure out bbox and contained images -----------------------------
            
            sw = self.layer.projection.projLocation(Point(xmin, ymin))
            ne = self.layer.projection.projLocation(Point(xmax, ymax))
            
            bbox = sw.lon, sw.lat, ne.lon, ne.lat
            images = self.client.images_by_bbox(bbox)
            images = map(localize_image_path, images)
            
            # Set up a target oam.Image ----------------------------------------
            
            handle, junkpath = mkstemp(prefix='oamtiles-', suffix='.vrt')
            garbage.append(junkpath)
            close(handle)
            
            target = oam.Image(junkpath, bbox, width, height, crs=images[0].crs)
            
            # Build input gdal datasource --------------------------------------
            
            vrtdoc = build_vrt(target, images)

            handle, vrtpath = mkstemp(prefix='oamtiles-', suffix='.vrt')
            garbage.append(vrtpath)
            close(handle)
            
            vrtfile = open(vrtpath, 'w')
            vrtdoc.writexml(vrtfile, encoding='utf-8')
            vrtfile.close()
            
            source_ds = gdal.Open(vrtpath)
            
            assert source_ds, \
                "oam.tiles.Provider couldn't open the file: %s" % vrtpath
            
            # Prepare output gdal datasource -----------------------------------
        
            handle, areapath = mkstemp(prefix='oamtiles-', suffix='.tif')
            garbage.append(areapath)
            close(handle)
            
            driver = gdal.GetDriverByName('GTiff')
            destination_ds = driver.Create(areapath, width, height, 3)

            assert destination_ds is not None, \
                "oam.tiles.Provider couldn't make the file: %s" % areapath
            
            merc = osr.SpatialReference()
            merc.ImportFromProj4(srs)
            destination_ds.SetProjection(merc.ExportToWkt())
    
            # note that 900913 points north and east
            x, y = xmin, ymax
            w, h = xmax - xmin, ymin - ymax
            
            gtx = [x, w/width, 0, y, 0, h/height]
            destination_ds.SetGeoTransform(gtx)
            
            # Create rendered area ---------------------------------------------
            
            gdal.ReprojectImage(source_ds, destination_ds)
            
            r, g, b = [destination_ds.GetRasterBand(i).ReadRaster(0, 0, width, height) for i in (1, 2, 3)]
            data = ''.join([''.join(pixel) for pixel in zip(r, g, b)])
            area = PIL.Image.fromstring('RGB', (width, height), data)
    
        finally:
            for filename in garbage:
                unlink(filename)

        return area
    
    def getTypeByExtension(self, extension):
        """ Return (image/jpeg, JPEG) for extension "jpg", throw error for anything else.
        """
        if extension == 'jpg':
            return ('image/jpeg', 'JPEG')

        raise KnownUnknown('oam.tiles.Provider only wants to make "jpg" tiles, not "%s"' % extension)

def localize_image_path(image):
    """ Currently a no-op, this function is a placeholder for locally caching remote files.
    """
    return deepcopy(image)

def build_vrt(target, images):
    """ Make an XML DOM representing a VRT.
    
        Use a target image and a collection of source images to mosaic.
    """
    impl = getDOMImplementation()
    doc = impl.createDocument(None, 'VRTDataset', None)
    
    root = doc.documentElement
    root.setAttribute('rasterXSize', str(target.width))
    root.setAttribute('rasterYSize', str(target.height))
    
    gt = doc.createElement('GeoTransform')
    gt.appendChild(doc.createTextNode(', '.join(['%.16f' % x for x in target.transform])))
    
    lonlat = osr.SpatialReference()
    lonlat.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    
    srs = doc.createElement('SRS')
    srs.appendChild(doc.createTextNode(lonlat.ExportToWkt()))
    
    root.appendChild(gt)
    root.appendChild(srs)
    
    for (band, interp) in zip((1, 2, 3), ('Red', 'Green', 'Blue')):
    
        rb = doc.createElement('VRTRasterBand')
        rb.setAttribute('dataType', 'Band')
        rb.setAttribute('band', str(band))
    
        ci = doc.createElement('ColorInterp')
        ci.appendChild(doc.createTextNode(interp))

        rb.appendChild(ci)
        root.appendChild(rb)
        
        for image in images:
        
            overlap = image.intersection(target.bbox)
            image_win = image.window(overlap)
            target_win = target.window(overlap)
            
            band_idx, data_type, block_width, block_height = image.bands[interp]
            
            cs = doc.createElement('ComplexSource')
            
            sf = doc.createElement('SourceFilename')
            sf.setAttribute('relativeToVRT', '0')
            sf.appendChild(doc.createTextNode('/vsicurl/' + image.path))
            
            sb = doc.createElement('SourceBand')
            sb.appendChild(doc.createTextNode(str(band)))
            
            nd = doc.createElement('NODATA')
            nd.appendChild(doc.createTextNode('0'))
            
            sp = doc.createElement('SourceProperties')
            sp.setAttribute('RasterXSize', str(image.width))
            sp.setAttribute('RasterYSize', str(image.height))
            sp.setAttribute('DataType', data_type)
            sp.setAttribute('BlockXSize', str(block_width))
            sp.setAttribute('BlockYSize', str(block_height))

            sr = doc.createElement('SrcRect')
            sr.setAttribute('xOff', str(image_win[0]))
            sr.setAttribute('yOff', str(image_win[1]))
            sr.setAttribute('xSize', str(image_win[2]))
            sr.setAttribute('ySize', str(image_win[3]))

            dr = doc.createElement('DstRect')
            dr.setAttribute('xOff', str(target_win[0]))
            dr.setAttribute('yOff', str(target_win[1]))
            dr.setAttribute('xSize', str(target_win[2]))
            dr.setAttribute('ySize', str(target_win[3]))

            cs.appendChild(sf)
            cs.appendChild(sb)
            cs.appendChild(nd)
            cs.appendChild(sp)
            cs.appendChild(sr)
            cs.appendChild(dr)
            rb.appendChild(cs)

    return doc

if __name__ == '__main__':
    pass
