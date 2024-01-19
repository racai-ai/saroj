#!/bin/sh

rm -f mapping7.map
touch mapping7.map

curl \
    --trace-ascii trace7.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityMapping/test6_in.conllup\",\"output\":\"/data/SAROJ/tests_EntityMapping/test7_out.conllup\",\"mapping\":\"/data/SAROJ/tests_EntityMapping/mapping7.map\"}" \
    http://127.0.0.1:8002/process

