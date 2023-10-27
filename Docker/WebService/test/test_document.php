<?php

require_once "send_data.php";

$ret=sendData("http://127.0.0.1:8111/startAnonymization.php",
[ "input" => json_encode([
    "caseid" => "CASE1",
    "docid" => "DOCID1",
    "document" => base64_encode(file_get_contents("test1.docx"))
])]);

var_dump($ret);
