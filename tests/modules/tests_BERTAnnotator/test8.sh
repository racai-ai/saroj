#!/bin/sh

curl \
    --trace-ascii trace8.log \
    -s -X POST \
    -F "input={\"input\":\"/data/SAROJ/tests_BERTAnnotator/test8_in.conllup\",\"output\":\"/data/SAROJ/tests_BERTAnnotator/test8_out.conllup\"}" \
    http://127.0.0.1:8002/process

