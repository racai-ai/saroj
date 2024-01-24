#!/bin/sh

curl \
    --trace-ascii trace15.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/symbols.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/symbols.out\"}" \
    http://127.0.0.1:8002/process

