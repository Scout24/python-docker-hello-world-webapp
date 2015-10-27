from bottle import route, run
from socket import gethostbyname, gethostname
#from bottledaemon import daemon_run

__version__ = '${build_version}'


@route("/")
def hello_world():
    return "<h2>Hello World!</h2><br/><b>Build Version:</b> <i>{0}</i>".format(__version__)


def run_server():
    run(host="0.0.0.0", port=8080)

if __name__ == '__main__':
    run_server()
