from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from hello_world import __version__

PORT_NUMBER = 8080

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Send the html message
        self.wfile.write(str("Hello World !\nVersion:", __version__))
        return

class MyServer:
    
    def start(self):
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
        