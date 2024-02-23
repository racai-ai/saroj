#!/bin/sh

curl \
    --trace-ascii trace18.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test18.in\",\"output\":\"/data/SAROJ/tests_TextExtractor/test18.out\",\"type\":\"txt\"}" \
    http://127.0.0.1:8002/process

