FROM docker.devops.app.vanderbilt.edu/vuit-commons/python:3.10-2402.0.0

USER root
ADD requirements.txt ./
ADD --chown=batch:batch src/python/* ./

ADD requirements.txt ./
ARG DOCKER_ARGS_PYPI_INDEX
RUN pip install --no-cache-dir -r requirements.txt -i $DOCKER_ARGS_PYPI_INDEX

RUN chown batch:batch executeApp.sh && \
  chmod 750 ./main.py

USER batch
