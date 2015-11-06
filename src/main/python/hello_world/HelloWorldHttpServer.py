from bottle import run, default_app

__version__ = '${build_version}'

app = default_app()

@app.route("/")
def hello_world():
    return "<html><body><h2>Hello World!</h2><br/><b>Build Version:</b> <i>{0}</i></body></html>"\
        .format(__version__)


def run_server(): #pragma: no cover
    run(host="0.0.0.0", port=8080, server="tornado")

if __name__ == '__main__': #pragma: no cover
    run_server()
