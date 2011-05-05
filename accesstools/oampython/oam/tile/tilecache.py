from TileCache.Layer import MetaLayer

from urlparse import urljoin
from copy import deepcopy
from xml.dom.minidom import getDOMImplementation

import os
# Make sure that GDAL doesn't attempt to GetFileList over /vsicurl/
# as this can get very slow when directory listings are lengthy.
os.environ["GDAL_DISABLE_READDIR_ON_OPEN"]="YES"

import oam

try:
    from PIL import Image
except ImportError:
    import Image

try:
    from osgeo import gdal
    from osgeo import osr
except ImportError:
    # well it won't work but we can still make the documentation.
    pass

class OAM(MetaLayer):
    def __init__ (self, name, **kwargs):
        MetaLayer.__init__(self, name, **kwargs) 
        self.client = oam.Client(username, password)

    def renderTile(self, tile):
        driver = gdal.GetDriverByName('GTiff')
        images = self.client.images_by_bbox(tile.bounds(), output='full')
            
        if not images: return None
        
        # Set up a target oam.Image ----------------------------------------
        target = oam.Image("unused", tile.bbox, tile.width, tile.height,
                            crs=images[0].crs)
        
        # Build input gdal datasource --------------------------------------
        vrtdoc = self.build_vrt(target, images)
        vrt = vrtdoc.toxml('utf-8')
        source_ds = gdal.Open(vrt)
        
        assert source_ds, \
            "%s couldn't open the VRT: %s" % (type(self),vrt)
        
        # Prepare output gdal datasource -----------------------------------
        try:
            destination_ds = driver.Create('/vsimem/output', width, height, 3)

            assert destination_ds is not None, \
                "%s couldn't make the file: /vsimem/output" % type(self)
            
            merc = osr.SpatialReference()
            merc.ImportFromProj4(srs)
            destination_ds.SetProjection(merc.ExportToWkt())

            # note that 900913 points north and east
            x, y = xmin, ymax
            w, h = xmax - xmin, ymin - ymax
            
            gtx = [x, w/width, 0, y, 0, h/height]
            destination_ds.SetGeoTransform(gtx)
            
            # Create rendered area -------------------------------------
            gdal.ReprojectImage(source_ds, destination_ds)
            
            r, g, b = [destination_ds.GetRasterBand(i).ReadRaster(0, 0, width, height) for i in (1, 2, 3)]
            data = ''.join([''.join(pixel) for pixel in zip(r, g, b)])
            area = Image.fromstring('RGB', (width, height), data)

            buffer = StringIO.StringIO()
            area.save(buffer, self.extension)
            buffer.seek(0)
            tile.data = buffer.read()

        finally:
            driver.Delete("/vsimem/output")

    return tile.data

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
