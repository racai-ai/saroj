#!/bin/sh

curl \
    --trace-ascii trace3.log \
    -s -X POST \
    -F "input={\"input\":[\"/data/xxxx.docx\"],\"output\":\"/data/xxxx.out1\"}" \
    http://127.0.0.1:8002/process

