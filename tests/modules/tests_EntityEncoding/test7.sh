#!/bin/sh

curl \
    --trace-ascii trace7.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityEncoding/test7_in2.conllup\",\"output\":\"/data/SAROJ/tests_EntityEncoding/test7_out.conllup\",\"mapping\":\"/data/SAROJ/tests_EntityEncoding/mapping7.out\"}" \
    http://127.0.0.1:8002/process

