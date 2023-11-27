#!/bin/sh

mkdir -p /data/tmp/SAROJ-run/logs/apache2
mkdir -p /data/tmp/SAROJ-run/data
mkdir -p /data/tmp/SAROJ-run/data/tasks
mkdir -p /data/tmp/SAROJ-run/data/tasks/new
mkdir -p /data/tmp/SAROJ-run/data/tasks/done
mkdir -p /data/tmp/SAROJ-run/data/tasks/run
mkdir -p /data/tmp/SAROJ-run/data/cases

if [ ! -f /data/tmp/SAROJ-run/data/config.json ]; then
    cp test/config.json /data/tmp/SAROJ-run/data/config.json
fi

if [ ! -f /data/tmp/SAROJ-run/data/udpipe.model.ud ]; then
    cp test/udpipe.model.ud /data/tmp/SAROJ-run/data/udpipe.model.ud
fi

docker run --name "saroj-run" -d -p=8111:80 \
    -v /data/tmp/SAROJ-run/logs:/var/log \
    -v /data/tmp/SAROJ-run/data:/data \
    saroj

docker ps

