from bottle import run, default_app

__version__ = '${build_version}'

app = default_app()


@app.route('/')
@app.route('/<name>')
def hello_world(name='World'):
    return ('<html><body><h2>Hello {0}!</h2>'
            '<br/><b>Build Version:</b>'
            ' <i>{1}</i></body></html>').format(name, __version__)


def run_server():  # pragma: no cover
    run(host="0.0.0.0", port=8080, server="paste")

if __name__ == '__main__':  # pragma: no cover
    run_server()
