#!/bin/sh

rm -f mapping6.map
cp mapping6.map_orig mapping6.map

curl \
    --trace-ascii trace6.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_EntityMapping/test6_in.conllup\",\"output\":\"/data/SAROJ/tests_EntityMapping/test6_out.conllup\",\"mapping\":\"/data/SAROJ/tests_EntityMapping/mapping6.map\"}" \
    http://127.0.0.1:8002/process

