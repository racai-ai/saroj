#!/bin/sh

curl \
    --trace-ascii trace10.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test10.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test10.out\"}" \
    http://127.0.0.1:8002/process

