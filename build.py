from pybuilder.core import use_plugin, init
from datetime import datetime

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("filter_resources")

name = "sample-app"
default_task = "publish"

version = "0.1 (" + datetime.now().strftime('%m %h %Y %H:%M:%S') + ")"

@init
def set_properties(project):
    project.set_property("filter_resources_glob", ['**/hello_world/__init__.py'])
    pass
