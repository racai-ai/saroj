#!/bin/sh

curl \
    --trace-ascii trace22.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test22.in\",\"output\":\"/data/SAROJ/tests_TextExtractor/test22.out\",\"type\":\"html\"}" \
    http://127.0.0.1:8002/process

