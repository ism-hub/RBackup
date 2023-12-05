FROM python:alpine

RUN apk add --no-cache \
    bash \
    rsync \
    openssh

RUN pip3 install pytest

COPY ./config /config
COPY ./config /config_org
COPY ./src /src
COPY ./tests /tests
COPY ./entrypoint.sh /entrypoint.sh
COPY ./cron_script.py /cron_script.py

ENV REAL_RUN=1

ENTRYPOINT ["/bin/bash", "entrypoint.sh"]
