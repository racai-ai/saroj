#!/bin/sh

curl \
    --trace-ascii trace9.log \
    -s -X POST \
    -F "input={\"original\":\"/data/SAROJ/tests_TextReconstruction/ro.docx\",\"input\":\"/data/SAROJ/tests_TextReconstruction/ro_in.conllup\",\"output\":\"/data/SAROJ/tests_TextReconstruction/ro_out.docx\"}" \
    http://127.0.0.1:8002/process

