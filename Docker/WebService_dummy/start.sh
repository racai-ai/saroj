#!/bin/sh

mkdir -p /data/tmp/SAROJDUMMY-run/logs/apache2

docker run --name "sarojdummy-run" -d -p=8111:80 \
    -v /data/tmp/SAROJDUMMY-run/logs:/var/log \
    sarojdummy

docker ps

