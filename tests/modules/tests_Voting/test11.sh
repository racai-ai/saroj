#!/bin/sh

curl \
    --trace-ascii trace11.log \
    -s -X POST \
    -F "input={\"input\":[\"/data/SAROJ/tests_Voting/test11_in1.conllup\",\"/data/SAROJ/tests_Voting/test11_in2.conllup\"],\"output\":\"/data/SAROJ/tests_Voting/test11_out.conllup\"}" \
    http://127.0.0.1:8002/process

