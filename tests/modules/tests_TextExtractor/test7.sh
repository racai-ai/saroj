#!/bin/sh

curl \
    --trace-ascii trace7.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test2.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test7.out\"}" \
    http://127.0.0.1:8002/process

