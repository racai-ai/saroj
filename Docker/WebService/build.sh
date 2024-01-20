#!/bin/sh

docker build --tag saroj .


docker rmi -f $(docker images -q --filter label=stage=intermediate)
