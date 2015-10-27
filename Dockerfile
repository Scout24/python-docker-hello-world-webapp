FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:/code/

RUN mkdir -p /code/hello_world
RUN pip install bottle
WORKDIR /code
ADD target/dist/python-docker-hello-world-webapp*/scripts /code/
ADD target/dist/python-docker-hello-world-webapp*/hello_world /code/hello_world

ENTRYPOINT ["python", "/code/server"]
