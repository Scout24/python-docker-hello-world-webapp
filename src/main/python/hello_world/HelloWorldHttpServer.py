from bottle import route, run
import socket

__version__ = '${build_version}'


@route("/")
def hello_world():
    return "<h2>Hello World!</h2><br/><b>Build Version:</b> <i>{0}</i>".format(__version__)


def run_server():
    run(host=socket.gethostname(), port=8080)

if __name__ == '__main__':
    run_server()
