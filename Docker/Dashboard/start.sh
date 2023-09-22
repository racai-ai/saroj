#!/bin/sh

mkdir -p /data/tmp/SAROJ-DASHBOARD-run/logs
mkdir -p /data/tmp/SAROJ-DASHBOARD-run/logs/apache2

# /data/tmp/RELATE-run/corpora este calea catre corpora din RELATE

docker run --name "SAROJ-DASHBOARD-run" -d -p=8001:80 \
    -v /data/tmp/RELATE-run/corpora:/site/DB/corpora \
    -v /data/tmp/SAROJ-DASHBOARD-run/logs:/var/log \
    saroj_dashboard

docker ps

