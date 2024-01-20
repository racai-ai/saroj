#!/bin/sh

curl \
    --trace-ascii trace11.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test11.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test11.out\"}" \
    http://127.0.0.1:8002/process

