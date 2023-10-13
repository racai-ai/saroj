#!/bin/sh

docker build --tag saroj_dashboard .


#docker rmi -f $(docker images -q --filter label=stage=intermediate)
