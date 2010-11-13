from oam.client import Client, default_service
from oam.image import Image
import unittest, sys,  json

class MockHTTPClient(object):
    def __init__(self):
        self.response = "{}"

    def open(self, request):
        self.method = request.get_method()
        self.url = request.get_full_url()
        self.data = request.get_data()
        return self

    def read(self):
        return self.response

class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client("user", "password")
        self.client.http = MockHTTPClient()

    def test__init__(self):
        self.assertEquals(self.client.user, "user")
        self.assertEquals(self.client.password, "password")
        self.assertEquals(self.client.service, default_service)
        self.assertEquals(self.client.verbose, False)
        self.assertEquals(self.client.test, False)
        client = Client("user", "password", "http://wherever", True, True)
        self.assertEquals(client.service, "http://wherever/")
        self.assertEquals(client.verbose, True)
        self.assertEquals(client.test, True)

    def test_request(self):
        result = self.client.request("GET", "whatever")
        self.assertEquals(self.client.http.method, "GET")
        self.assertEquals(self.client.http.url, default_service + "whatever")
        self.assertEquals(self.client.http.data, None)
        self.assertEquals(result, {})
        
        result = self.client.request("GET", "whatever", {"key": "value"})
        self.assertEquals(self.client.http.url, default_service + "whatever?key=value")
        self.assertEquals(self.client.http.data, None)

        result = self.client.request("POST", "whatever", {"key": "value"})
        self.assertEquals(self.client.http.method, "POST")
        self.assertEquals(self.client.http.url, default_service + "whatever")
        self.assertEquals(self.client.http.data, '{"key": "value"}')

        self.client.http.response = "{'error': 'oops!'}"
        self.assertRaises(Exception, self.client.request, "POST", "whatever", {"key": "value"})
    
    def test_layer(self):
        result = self.client.layer(6)
        self.assertEquals(self.client.http.method, "GET")
        self.assertEquals(self.client.http.url, default_service + "layer/6")
        self.assertEquals(self.client.http.data, None)
        self.assertEquals(result, {})

        self.client.layer(6, archive="true")
        self.assertEquals(self.client.http.url, default_service + "layer/6?archive=true")
    
    def test_image(self):
        image = Image("http://wherever/wtf.png", (-180, -90, 180, 90), 400, 200)
        self.client.http.response = json.dumps(image.to_dict())
        result = self.client.image(7)
        self.assertEquals(self.client.http.method, "GET")
        self.assertEquals(self.client.http.url, default_service + "image/7")
        self.assertEquals(self.client.http.data, None)
        self.assertEquals(result.path, image.path)
        self.assertEquals(result.bbox, image.bbox)
        self.assertEquals(result.width, image.width)
        self.assertEquals(result.height, image.height)

        result = self.client.image(7, archive="true")
        self.assertEquals(self.client.http.method, "GET")
        self.assertEquals(self.client.http.url, default_service + "image/7?archive=true")
        self.assertEquals(self.client.http.data, None)

    def test_images_by_bbox(self):
        images = [
            Image("http://wherever/wtf1.png", (-180, -90, 180, 90), 400, 200),
            Image("http://wherever/wtf2.png", (-90, -90, 0, 90), 350, 100),
            Image("http://wherever/wtf3.png", (-90, 0, 90, 90), 5400, 4200)
        ]
        self.client.http.response = json.dumps({"images": [image.to_dict() for image in images]})

        result = self.client.images_by_bbox((-180, -90, 180, 90))
        self.assertEquals(self.client.http.method, "GET")
        self.assertEquals(self.client.http.url, default_service + "image/?bbox=-180.000000%2C-90.000000%2C180.000000%2C90.000000")
        self.assertEquals(self.client.http.data, None)

        result = self.client.images_by_bbox((-180, -90, 180, 90), archive="true")
        self.assertEquals(self.client.http.method, "GET")
        self.assertEquals(self.client.http.url, default_service + "image/?archive=true&bbox=-180.000000%2C-90.000000%2C180.000000%2C90.000000")
        self.assertEquals(self.client.http.data, None)

    def test_save_image(self):
        image = Image("http://wherever/wtf1.png", (-180, -90, 180, 90), 400, 200)
        result = self.client.save_image(image)
        self.assertEquals(self.client.http.method, "POST")
        self.assertEquals(self.client.http.url, default_service + "image/")
        self.assertEquals(self.client.http.data, json.dumps(image.to_dict()))
        self.assertEquals(result, {})

if __name__ == "__main__":
    unittest.main()
