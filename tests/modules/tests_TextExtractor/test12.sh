#!/bin/sh

curl \
    --trace-ascii trace12.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_empty.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test12.out\"}" \
    http://127.0.0.1:8002/process

