#!/bin/sh

curl -s \
    --trace-ascii trace13.log \
    -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_empty2.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test13.out\"}" \
    http://127.0.0.1:8002/process

