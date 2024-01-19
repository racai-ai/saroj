#!/bin/sh

curl \
    --trace-ascii trace16.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/ro.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/ro.out\"}" \
    http://127.0.0.1:8002/process

