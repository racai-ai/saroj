#!/bin/sh

curl \
    --trace-ascii trace20.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_TextExtractor/test_despartire_tokeni.docx\",\"output\":\"/data/SAROJ/tests_TextExtractor/test20.out\"}" \
    http://127.0.0.1:8002/process

