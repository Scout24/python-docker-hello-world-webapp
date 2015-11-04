from __future__ import print_function

from datetime import datetime
from textwrap import dedent
from string import Template

import os
from pybuilder.core import use_plugin, init, task, depends
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
    project.depends_on("tornado")
    project.build_depends_on("webtest")
    project.build_depends_on("docker-py")
    project.build_depends_on("sh")

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
        'bucket_name', os.environ.get('BUCKET_NAME_FOR_UPLOAD'))
    project.set_property(
        'lambda_file_access_control',
        os.environ.get('LAMBDA_FILE_ACCESS_CONTROL'))


def check_sh(logger):
    """ Check if 'sh' module is installed'. """
    if not sh:
        logger.error("The 'sh' module was not found!")
        logger.error("Run 'pyb install_dependencies' to enable this task.")
        raise BuildFailedException('Unable to run task!')


def docker_execute(command_list, logger):
    """ Run and tail a docker command. """
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
    check_sh(logger)
    logger.info("Building the docker image: {0}".format(docker_image_label()))
    docker_execute(['build', '-t', docker_image_label(),
                    project.expand_path("$dir_target")], logger)


@task
@depends("docker_build")
def docker_push(logger):
    check_sh(logger)
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
    check_sh(logger)
    logger.info("Will now attempt remove the docker image.")
    docker_execute(['rmi', docker_image_label()], logger)


def upload_helper(project, logger, bucket_name, keyname, data):
    import boto3
    s3 = boto3.resource('s3')
    logger.info("Uploading cfn.json to bucket: '{0}' as key: '{1}'".
                format(bucket_name, keyname))
    acl = project.get_property('lambda_file_access_control')
    s3.Bucket(bucket_name).put_object(
        Key=keyname, Body=data, ACL=acl)


@task('build_json',
      description='Convert & upload CFN JSON from the template YAML files')
def build_json(project, logger):
    from cfn_sphere.aws.cloudformation.template_loader import (
        CloudFormationTemplateLoader)
    from cfn_sphere.aws.cloudformation.template_transformer import (
        CloudFormationTemplateTransformer)

    template = CloudFormationTemplateLoader.get_template_from_url(
        'bootstrap.yml', 'cfn/templates')
    transformed = CloudFormationTemplateTransformer.transform_template(
        template)
    output = transformed.get_template_json()

    bucket_name = project.get_property('bucket_name')
    version_path = 'v{0}/{1}.json'.format(project.version, project.name)
    latest_path = 'latest/{0}.json'.format(project.name)

    upload_helper(project, logger, bucket_name, version_path, output)
    upload_helper(project, logger, bucket_name, latest_path, output)
