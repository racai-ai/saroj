#!/bin/sh

curl \
    --trace-ascii trace7.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_RegexAnnotator/test7_in2.conllup\",\"output\":\"/data/SAROJ/tests_RegexAnnotator/test7_out.conllup\"}" \
    http://127.0.0.1:8002/process

