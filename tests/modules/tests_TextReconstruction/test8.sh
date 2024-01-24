#!/bin/sh

curl \
    --trace-ascii trace8.log \
    -s -X POST \
    -F "input={\"original\":\"/data/SAROJ/tests_TextReconstruction/test_empty.docx\",\"input\":\"/data/SAROJ/tests_TextReconstruction/test8_in.conllup\",\"output\":\"/data/SAROJ/tests_TextReconstruction/test8_out.docx\"}" \
    http://127.0.0.1:8002/process

