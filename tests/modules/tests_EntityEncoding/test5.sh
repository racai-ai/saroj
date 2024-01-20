#!/bin/sh

curl \
    --trace-ascii trace5.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityEncoding/test5.sh\",\"output\":\"/data/SAROJ/tests_EntityEncoding/test5.out\",\"mapping\":\"/data/SAROJ/tests_EntityEncoding/mapping5.out\"}" \
    http://127.0.0.1:8002/process

