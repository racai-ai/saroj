#!/bin/sh

curl \
    --trace-ascii trace8.log \
    -s -X POST \
    -F "input={\"input\":[\"/data/SAROJ/tests_Voting/test8_in1.conllup\",\"/data/SAROJ/tests_Voting/test8_in2.conllup\",\"/data/SAROJ/tests_Voting/test8_in3.conllup\"],\"output\":\"/data/SAROJ/tests_Voting/test8_out.conllup\"}" \
    http://127.0.0.1:8002/process

