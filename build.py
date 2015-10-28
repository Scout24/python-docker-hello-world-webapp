from __future__ import print_function

from datetime import datetime

from pybuilder.core import use_plugin, init, task
from pybuilder.errors import BuildFailedException


try:
    import sh  # conditional import, make pyb work w/o it being installed
except ImportError:
    sh = None

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("filter_resources")

org_name = "immobilienscout24"
name = "python-docker-hello-world-webapp"
version = "0.2.3"
default_task = ['analyze', 'publish']

summary = 'Simple Hello World Webapp!'
description = """tbd."""
url = 'https://github.com/ImmobilienScout24/python-docker-hello-world-webapp'
license = 'Apache License 2.0'

build_version = name + " " + version + " (" + datetime.now().strftime('%d %h %Y %H:%M:%S') + ")"

@init
def set_properties(project):
    project.set_property("verbose", True)

    project.depends_on("bottle")
    project.depends_on("tornado")
    project.build_depends_on("webtest")
    project.build_depends_on("docker-py")
    project.build_depends_on("sh")

    project.set_property("name", name)
    project.set_property("version", version)
    project.set_property("build_version", build_version)
    project.set_property("filter_resources_glob", ['**/hello_world/HelloWorldHttpServer.py'])
    project.set_property("dir_dist", "$dir_target/dist/$name-$version")

    project.set_property("flake8_include_test_sources", True)
    project.set_property('coverage_break_build', False)

    project.set_property("install_dependencies_upgrade", True)

    project.set_property('copy_resources_target', '$dir_dist')
    project.set_property('dir_dist_scripts', 'scripts')

    project.set_property('distutils_classifiers', [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: System :: Networking'
    ])


def check_sh(logger):
    """ Check if 'sh' module is installed'. """
    if not sh:
        logger.error("The 'sh' module was not found!")
        logger.error("Run 'pyb install_dependencies' to enable this task.")
        raise BuildFailedException('Unable to run task!')


def docker_execute(command_list):
    """ Run and tail a docker command. """
    running_command = sh.docker(command_list)
    for line in running_command:
        print(line.strip())


@task
def docker_build(logger):
    check_sh(logger)
    logger.info("Will now attempt to build the docker image.")
    docker_execute(['build', '-t',
                    '{0}/{1}:{2}'.format(org_name, name, version), '.'])


@task
def docker_rmi(logger):
    check_sh(logger)
    logger.info("Will now attempt remove the docker image.")
    docker_execute(['rmi', '{0}/{1}:{2}'.format(org_name, name, version)])
