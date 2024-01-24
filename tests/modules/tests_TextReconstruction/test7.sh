#!/bin/sh

curl \
    --trace-ascii trace7.log \
    -s -X POST \
    -F "input={\"original\":\"/data/SAROJ/tests_TextReconstruction/test2.docx\",\"input\":\"/data/SAROJ/tests_TextReconstruction/test7_in2.conllup\",\"output\":\"/data/SAROJ/tests_TextReconstruction/test7_out.docx\"}" \
    http://127.0.0.1:8002/process

