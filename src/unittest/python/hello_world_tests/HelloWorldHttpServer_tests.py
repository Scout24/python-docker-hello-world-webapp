import unittest

from hello_world.HelloWorldHttpServer import app
import webtest

test_app = webtest.TestApp(app)


class HelloWorldTests(unittest.TestCase):

    def test_hello_world(self):
        resp = test_app.get("/")
        self.assertEqual(
            resp.text, "<html><body><h2>Hello World!</h2><br/><b>Build Version:</b> <i>${build_version}</i></body></html>")
        self.assertEqual(resp.status, '200 OK')
