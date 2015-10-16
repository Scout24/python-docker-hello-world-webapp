from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from hello_world import __version__

PORT_NUMBER = 8080


class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write("<h2>Hello World!</h2><br/><b>Build Version:</b> <i>" + __version__ + "</i>")
        return

def start_server():
    """
    Starts a simple HTTP server that publishes "Hello World" together with its build version

    :rtype : void
    """
    try:
        #Create a web server and define the handler to manage the
        #incoming request
        server = HTTPServer(('', PORT_NUMBER), MyHandler)
        print 'Started httpserver on port ', PORT_NUMBER

        #Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print '^C received, shutting down the web server'
        server.socket.close()
