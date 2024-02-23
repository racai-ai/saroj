#!/bin/sh

curl \
    --trace-ascii trace10.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityEncoding/test10_in.conllup\",\"output\":\"/data/SAROJ/tests_EntityEncoding/test10_out.conllup\",\"mapping\":\"/data/SAROJ/tests_EntityEncoding/mapping7.out\"}" \
    http://127.0.0.1:8002/process

