#!/bin/sh

curl \
    --trace-ascii trace17.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_space2.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test_space2.out\"}" \
    http://127.0.0.1:8002/process

