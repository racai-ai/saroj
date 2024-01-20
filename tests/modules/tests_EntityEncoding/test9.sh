#!/bin/sh

cp -f mapping8.out mapping9.out

curl \
    --trace-ascii trace9.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityEncoding/test9_in.conllup\",\"output\":\"/data/SAROJ/tests_EntityEncoding/test9_out.conllup\",\"mapping\":\"/data/SAROJ/tests_EntityEncoding/mapping9.out\"}" \
    http://127.0.0.1:8002/process

