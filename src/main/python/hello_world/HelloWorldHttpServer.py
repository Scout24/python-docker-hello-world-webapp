from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import TCPServer
import threading
import functools
import socket
from contextlib import contextmanager

__version__ = '${build_version}'

# "<h2>Hello World!</h2><br/><b>Build Version:</b> <i>" + __version__ + "</i>"

class HelloWorldHandler(BaseHTTPRequestHandler):
    """
    Http-Handler for our simple "Hello World" example, serves content on a GET request.

    :rtype : void
    """

    def do_GET(self):
        """
        Serve Hello World and the build version.
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write()
        return

@contextmanager
def start_server(port=0, fork=True):
    """
    Starts a simple HTTP server that publishes "Hello World" together with its build version

    :rtype : void
    """
    def url(lport, lpath):
        address = 'http://%s:%s%s' % (socket.gethostname(), lport, lpath)
        print address
        return address

    # Create a web server and define the handler to manage the incoming request
    server = TCPServer(('', port), HelloWorldHandler)
    print 'Started httpserver on port ', server.server_address[1]

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(fork)
    t.start()

    port = server.server_address[1]
    yield functools.partial(url, port)
    server.shutdown()
