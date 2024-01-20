#!/bin/sh

curl \
    --trace-ascii trace2.log \
    -s -X POST \
    -F "input=\"\"" \
    http://127.0.0.1:8002/process

