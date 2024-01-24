#!/bin/sh

curl \
    --trace-ascii trace14.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_space.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test_space.out\"}" \
    http://127.0.0.1:8002/process

