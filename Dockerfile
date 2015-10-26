FROM python:2.7

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH $PYTHONPATH:/code/

RUN mkdir -p /code/hello_world
RUN pip install bottle bottledaemon
WORKDIR /code
ADD target/dist/sample-app*/scripts /code/
ADD target/dist/sample-app*/hello_world /code/hello_world

EXPOSE 8080:8080

CMD python /code/server start
