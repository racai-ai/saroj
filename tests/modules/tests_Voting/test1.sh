#!/bin/sh

curl \
    --trace-ascii trace1.log \
    -s -X POST \
    http://127.0.0.1:8002/process

