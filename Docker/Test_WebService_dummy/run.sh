#!/bin/sh

docker stop sarojtestsdummy-run
docker rm sarojtestsdummy-run

docker run --name "sarojtestsdummy-run" \
    -e "WSURL=http://127.0.0.1:8111/" \
    sarojtestsdummy


