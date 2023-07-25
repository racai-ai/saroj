#!/bin/sh

docker build --tag sarojdummy .


docker rmi -f $(docker images -q --filter label=stage=intermediate)
