#!/bin/sh

curl \
    --trace-ascii trace6.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_nume.docx\",\"output\":\"/data/SAROJ/tests_EntityEncoding/test6.out\",\"mapping\":\"/data/SAROJ/tests_EntityEncoding/mapping6.out\"}" \
    http://127.0.0.1:8002/process

