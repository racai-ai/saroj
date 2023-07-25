#!/bin/sh

docker stop sarojtestsdummy-run
docker rm sarojtestsdummy-run

docker run --name "sarojtestsdummy-run" -it sarojtestsdummy bash

