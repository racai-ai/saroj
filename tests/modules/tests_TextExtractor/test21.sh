#!/bin/sh

curl \
    --trace-ascii trace21.log \
    -s -X POST \
    -F "input={\"input\":\"/home/pvf/saroj_tests/run/input.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test21.out\"}" \
    http://127.0.0.1:8002/process

