#!/bin/sh

curl \
    --trace-ascii trace8.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityEncoding/test8_in.conllup\",\"output\":\"/data/SAROJ/tests_EntityEncoding/test8_out.conllup\",\"mapping\":\"/data/SAROJ/tests_EntityEncoding/mapping8.out\"}" \
    http://127.0.0.1:8002/process

