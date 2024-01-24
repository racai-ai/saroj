#!/bin/sh

curl \
    --trace-ascii traceh1.log \
    -s -X GET \
    http://127.0.0.1:8002/checkHealth

