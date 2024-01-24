#!/bin/sh

curl \
    --trace-ascii trace10.log \
    -s -X POST \
    -F "input={\"input\":[\"/data/SAROJ/tests_Voting/test10_in1.conllup\",\"/data/SAROJ/tests_Voting/test10_in2.conllup\"],\"output\":\"/data/SAROJ/tests_Voting/test10_out.conllup\"}" \
    http://127.0.0.1:8002/process

