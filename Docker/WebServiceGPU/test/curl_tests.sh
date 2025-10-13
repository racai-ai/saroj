#!/bin/sh

echo "Testing the WebService Docker with CURL"

echo "startAnonymization"
curl -X POST --trace-ascii trace1.log -F "input={}" http://127.0.0.1:8111/startAnonymization.php
echo ""

echo "getResult"
curl -X POST --trace-ascii trace2_post.log -F "input={\"id\":\"JOBID\"}" http://127.0.0.1:8111/getResult.php
echo ""

echo "getResult"
curl -X GET --trace-ascii trace2_get.log "http://127.0.0.1:8111/getResult.php?input=\{\"id\":\"JOBID\"\}"
echo ""

echo "doAnonymization"
curl -X POST --trace-ascii trace3.log -F "input={}" http://127.0.0.1:8111/doAnonymization.php
echo ""

echo "checkHealth"
curl -X GET --trace-ascii trace4.log http://127.0.0.1:8111/checkHealth.php
echo ""

echo "getVersion"
curl -X GET --trace-ascii trace5.log http://127.0.0.1:8111/getVersion.php
echo ""


