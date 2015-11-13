from __future__ import print_function

from datetime import datetime
from textwrap import dedent
from string import Template

import os
from pybuilder.core import use_plugin, init, task, depends


use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("filter_resources")
use_plugin("pypi:pybuilder_aws_lambda_plugin")

org_name = "immobilienscout24"
name = "python-docker-hello-world-webapp"
version = os.environ.get('BUILD_NUMBER', 0)
default_task = ['analyze', 'docker_push']

summary = 'Simple Hello World Webapp!'
description = """tbd."""
url = 'https://github.com/ImmobilienScout24/python-docker-hello-world-webapp'
license = 'Apache License 2.0'

build_version = "{0} {1} ({2})".format(
    name, version, datetime.now().strftime('%d %h %Y %H:%M:%S'))

dockerfile = dedent("""
    FROM python:2.7

    ENV PYTHONUNBUFFERED 1
    ENV PYTHONPATH $PYTHONPATH:/code/

    RUN mkdir -p /code/hello_world
    RUN pip install $PIP_EXTRA_ARGS bottle tornado
    WORKDIR /code
    ADD dist/python-docker-hello-world-webapp*/scripts /code/
    ADD dist/python-docker-hello-world-webapp*/hello_world /code/hello_world

    ENTRYPOINT ["python", "/code/server"]
""")


@init
def set_properties(project):
    project.set_property("verbose", True)

    project.depends_on("bottle")
    project.depends_on("paste")
    project.build_depends_on("webtest")
    project.build_depends_on("docker-py")
    project.build_depends_on("sh")
    project.build_depends_on("cfn-sphere")
    project.build_depends_on("boto3")

    project.set_property("name", name)
    project.set_property("version", version)
    project.set_property("build_version", build_version)
    project.set_property(
        "filter_resources_glob", ['**/hello_world/HelloWorldHttpServer.py'])
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

    project.set_property(
        'template_file_access_control', os.environ.get('CFN_FILE_ACCESS_CONTROL'))
    project.set_property('template_files',
                         [
                             ('cfn/templates/', 'alarm-topic.yml'),
                             ('cfn/templates/', 'ecs-simple-webapp'),
                             ('cfn/templates/', 'ecs-minimal-webapp')
                         ])

    project.set_property(
        'bucket_name', os.environ.get('BUCKET_NAME_FOR_UPLOAD'))
    project.set_property(
        'lambda_file_access_control',
        os.environ.get('LAMBDA_FILE_ACCESS_CONTROL'))


def docker_execute(command_list, logger):
    """ Run and tail a docker command. """
    import sh
    running_command = sh.docker(command_list, _iter=True)
    for line in running_command:
        logger.info(line.strip())


def docker_image_label():
    return '{0}/{1}:{2}'.format(org_name, name, version)


@task
@depends("package")
def generate_dockerfile(project, logger):
    logger.info("Building the Dockerfile")
    args = {"PIP_EXTRA_ARGS": os.environ.get('PIP_EXTRA_ARGS', '')}
    template = Template(dockerfile)
    rendered = template.safe_substitute(args)
    with open(os.path.join(project.expand_path("$dir_target"), "Dockerfile"), 'wb') as fp:
        fp.write(rendered)


@task
@depends("generate_dockerfile")
def docker_build(project, logger):
    logger.info("Building the docker image: {0}".format(docker_image_label()))
    docker_execute(['build', '-t', docker_image_label(),
                    project.expand_path("$dir_target")], logger)


@task
@depends("docker_build")
def docker_push(logger):
    docker_execute(['-D',
                    'login',
                    '-u', os.environ.get('DOCKER_USERNAME', 'unknown'),
                    '-p', os.environ.get('DOCKER_PASSWORD', 'unknown'),
                    '-e', os.environ.get('DOCKER_EMAIL', 'unknown')],
                   logger)
    docker_execute(['push', docker_image_label()], logger)
    docker_execute(['logout'], logger)


@task
def docker_rmi(logger):
    logger.info("Will now attempt remove the docker image.")
    docker_execute(['rmi', docker_image_label()], logger)


@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    project.set_property('teamcity_output', True)
    project.default_task = [
        'clean',
        'install_build_dependencies',
        'upload_cfn_to_s3',
        'docker_push'
    ]
    project.set_property('install_dependencies_index_url',
                         os.environ.get('PYPIPROXY_URL'))
