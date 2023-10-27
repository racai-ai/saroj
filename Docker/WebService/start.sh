#!/bin/sh

mkdir -p /data/tmp/SAROJ-run/logs/apache2
mkdir -p /data/tmp/SAROJ-run/data

docker run --name "saroj-run" -d -p=8111:80 \
    -v /data/tmp/SAROJ-run/logs:/var/log \
    -v /data/tmp/SAROJ-run/data:/data \
    saroj

docker ps

