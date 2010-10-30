from oam.image import Image, gdal
import unittest, os.path

def requires_gdal(method):
    def f(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except ImportError:
            self.failUnless(True, "Can't test GDAL-dependent methods without Python GDAL support.")
    return f

class ImageTest(unittest.TestCase):
    example_tif = os.path.join(os.path.dirname(__file__), "example.tif")
    epsg_4326 = """GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]]"""

    def fixture(self):
        return Image("http://oam.org/thingy", [-1.0, -1.0, 1.0, 1.0], 300, 200, file_format="GTiff")

    def test__init__(self):
        im = self.fixture()
        self.assertEqual(im.path, "http://oam.org/thingy")
        self.assertEqual(im.left, -1.0)
        self.assertEqual(im.bottom, -1.0)
        self.assertEqual(im.right, 1.0)
        self.assertEqual(im.top, 1.0)
        self.assertEqual(im.width, 300)
        self.assertEqual(im.height, 200)
        self.assertEqual(im.file_format, "GTiff")
        self.assertEqual(im.license, None)
        self.assertEqual(im.crs, None)
        self.assertRaises(AssertionError, Image, url="", bbox=[-1.0, -1.0, 1.0, 1.0], width=300, height=200)
        self.assertRaises(AssertionError, Image, url="stuff", bbox=[1.0, 1.0, -1.0, -1.0], width=300, height=200)
        self.assertRaises(AssertionError, Image, url="stuff", bbox=[1.0, 1.0, -1.0, -1.0], width=0, height=200)
        self.assertRaises(AssertionError, Image, url="stuff", bbox=[1.0, 1.0, -1.0, -1.0], width=300, height=0)

    @requires_gdal
    def test_load(self):
        im = Image.load(self.example_tif)
        self.assertEqual(im.path, self.example_tif)
        self.assertEqual([int(x*1e6) for x in im.bbox], [int(x*1e6) for x in (-72.3979813,  18.4507832, -72.3965384,  18.4522260)])
        self.assertEqual(im.file_format, "GTiff")
        self.assertEqual(im.width, 256)
        self.assertEqual(im.height, 256)
        self.assertEqual(im.crs, self.epsg_4326)
        self.assertTrue(im.vrt.startswith("<VRTDataset "))

    def test_computed_properties(self):
        im = self.fixture()
        self.assertEqual(im.px_width, 2.0/300)
        self.assertEqual(im.px_height, -2.0/200)
        self.assertEqual(im.transform, (-1.0, 2.0/300, 0.0, 1.0, 0.0, -2.0/200))
        self.assertEqual(im.bbox, (-1.0, -1.0, 1.0, 1.0))

    def test_window(self):
        im = self.fixture()
        self.assertEqual(im.window((0.0, 0.0, 1.0, 1.0)), (150, 0, 150, 100))

    def test_predicates(self):
        im = self.fixture()
        # identity
        self.assertEqual(im.intersection(im.bbox), im.bbox)
        # partial intersection
        self.assertEqual(im.intersection((0.0, 0.0, 2.0, 2.0)), (0.0, 0.0, 1.0, 1.0))
        # no intersection at all
        self.assertFalse(im.intersection((1.0, 1.0, 2.0, 2.0)))
        # full overlap
        self.assertEqual(im.union((0.0, 0.0, 1.0, 1.0)), im.bbox)
        # partial overlap
        self.assertEqual(im.union((0.0, 0.0, 2.0, 2.0)), (-1.0, -1.0, 2.0, 2.0))

    def test_to_dict(self):
        im = self.fixture()
        self.assertEqual(im.to_dict(), {
            "url": im.path,
            "file_format": im.file_format,
            "width": im.width,
            "height": im.height,
            "crs": im.crs,
            "license": im.license,
            "file_size": None,
            "hash": None,
            "vrt": im.vrt,
            "bbox": list(im.bbox)
        })

    @requires_gdal
    def test_load_vrt(self):
        im = Image.load(self.example_tif)
        self.assertTrue(im.load_vrt().startswith("<VRTDataset "))

    @requires_gdal
    def test_bands(self):
        im = Image.load(self.example_tif)
        self.assertEqual(im.bands, {'Blue': [3, 'Byte', 256, 16], 'Green': [2, 'Byte', 256, 16], 'Red': [1, 'Byte', 256, 16]})

if __name__ == "__main__":
    unittest.main()
