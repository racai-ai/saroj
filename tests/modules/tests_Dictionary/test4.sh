#!/bin/sh

curl \
    --trace-ascii trace4.log \
    -s -X GET \
    http://127.0.0.1:8002/process?input=%7B%22input%22%3A%22%2Fdata%2Fxxxx.docx%22%2C%22output%22%3A%22%2Fdata%2Fxxxx.out1%22%7D

