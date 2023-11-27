#!/bin/sh

echo "Testing the WebService Docker with CURL"

echo "startAnonymization"
curl -X POST -F "input={}" http://127.0.0.1:8111/startAnonymization.php
echo ""

echo "getResult"
curl -X POST -F "input={\"id\":\"JOBID\"}" http://127.0.0.1:8111/getResult.php
echo ""

echo "doAnonymization"
curl -X POST -F "input={}" http://127.0.0.1:8111/doAnonymization.php
echo ""

echo "checkHealth"
curl -X GET http://127.0.0.1:8111/checkHealth.php
echo ""

echo "getVersion"
curl -X GET http://127.0.0.1:8111/getVersion.php
echo ""


