#!/bin/sh

curl \
    --trace-ascii trace10.log \
    -s -X POST \
    -F "input={\"original\":\"/data/SAROJ/tests_TextReconstruction/test10.txt\",\"input\":\"/data/SAROJ/tests_TextReconstruction/test10.in\",\"output\":\"/data/SAROJ/tests_TextReconstruction/test10.out\",\"type\":\"txt\"}" \
    http://127.0.0.1:8002/process

