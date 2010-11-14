from tempfile import mkstemp
from os import close, unlink

import PIL.Image
import TileStache.Geography

try:
    from osgeo import gdal
    from osgeo import osr
except ImportError:
    # well it won't work but we can still make the documentation.
    pass

class Provider:
    
    def __init__(self, layer):
        self.layer = layer

    def renderArea(self, width, height, srs, xmin, ymin, xmax, ymax, zoom):
    
        garbage = []
        
        try:
            handle, filename = mkstemp(prefix='openaerialmap-', suffix='.tif')
            garbage.append(filename)
            close(handle)
            
            driver = gdal.GetDriverByName('GTiff')
            destination_ds = driver.Create(filename, width, height, 3)

            assert destination_ds is not None, \
                "OpenAerialMap.Provider couldn't make the file: %s" % filename
            
            merc = osr.SpatialReference()
            merc.ImportFromProj4(srs)
            destination_ds.SetProjection(merc.ExportToWkt())
    
            source_ds = gdal.Open('/home/migurski/public_html/oam-example.tif')
            
            x, y = xmin, ymax
            w, h = xmax - xmin, ymin - ymax # because 900913 points up
            
            gtx = [x, w/width, 0, y, 0, h/height]
            destination_ds.SetGeoTransform(gtx)
            
            gdal.ReprojectImage(source_ds, destination_ds)
            
            r, g, b = [destination_ds.GetRasterBand(i).ReadRaster(0, 0, width, height) for i in (1, 2, 3)]
            data = ''.join([''.join(pixel) for pixel in zip(r, g, b)])
            
            return PIL.Image.fromstring('RGB', (width, height), data)
    
        finally:
            for filename in garbage:
                unlink(filename)

if __name__ == '__main__':
    pass
