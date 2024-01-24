#!/bin/sh

curl \
    --trace-ascii trace8.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_aa.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test_aa.out\"}" \
    http://127.0.0.1:8002/process

