#!/bin/sh

docker stop sarojtestsdummy-run
docker rm sarojtestsdummy-run

hostip=$(ip addr show docker0 | grep -Po 'inet \K[\d.]+')

docker run --name "sarojtestsdummy-run" \
    -e "WSURL=http://$hostip:8111/" \
    sarojtestsdummy


