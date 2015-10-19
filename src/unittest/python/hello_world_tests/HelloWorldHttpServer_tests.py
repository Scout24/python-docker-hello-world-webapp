import unittest2
from hello_world.HelloWorldHttpServer import HelloWorldHandler, start_server
from StringIO import StringIO
import urllib2


class TestHelloWorldHandlerMethods(unittest2.TestCase):

    def test_do_GET(self):

        class MockRequest(object):

            def makefile(self, *args, **kwargs):
                return StringIO(b"GET /")

        class MockServer(object):

            def __init__(self, ip_port, Handler):
                Handler(MockRequest(), ip_port, self)

        MockServer(('0.0.0.0', 8888), HelloWorldHandler)


class TestStartServer(unittest2.TestCase):

    def test_start_server(self):

        with start_server() as url:
            print list(urllib2.urlopen(url("/")))
