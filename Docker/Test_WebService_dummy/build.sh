#!/bin/sh

docker build --tag sarojtestsdummy .


docker rmi -f $(docker images -q --filter label=stage=intermediate)
