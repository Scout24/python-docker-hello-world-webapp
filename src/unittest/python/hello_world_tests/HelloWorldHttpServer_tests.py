import unittest
import webtest
from hello_world import HelloWorldHttpServer
from bottle import default_app

app = default_app()

test_app = webtest.TestApp(app)


class HelloWorldTests(unittest.TestCase):

    def test_hello_world(self):
        resp = test_app.get("/")
        self.assertEqual(resp.text, "<h2>Hello World!</h2><br/><b>Build Version:</b> <i>${build_version}</i>")
        self.assertEqual(resp.status, '200 OK')

    def test_hello_world_not_equals(self):
        resp = test_app.get("/")
        self.assertNotEqual(resp.text, "<h2>Hello World!</h2><br/><b>Build Version:</b> <i></i>")
