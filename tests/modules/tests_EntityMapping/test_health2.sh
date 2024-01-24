#!/bin/sh

curl \
    --trace-ascii traceh2.log \
    -s -X POST \
    http://127.0.0.1:8002/checkHealth

