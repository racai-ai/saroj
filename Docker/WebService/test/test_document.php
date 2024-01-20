<?php

require_once "send_data.php";

echo "Start anonymization\n";
$ret=sendData("http://127.0.0.1:8111/startAnonymization.php",
[ "input" => json_encode([
    "caseid" => "CASE1",
    "docid" => "DOCID1",
    "document" => base64_encode(file_get_contents("test1.docx"))
])]);

echo "Result: ".var_export($ret,true)."\n";

$data=json_decode($ret,true);
$id=$data['id'];

while(true){
    $ret=file_get_contents("http://127.0.0.1:8111/getResult.php?input=".urlencode(json_encode(["id"=>$id])));
    var_dump($ret);
    $json=json_decode($ret,true);
    if( 
        isset($json['status']) && $json['status']=="OK" &&
        isset($json['result']) && $json['result']=="DONE" &&
        isset($json['document']) 
    ){
        file_put_contents("test1.out.docx",base64_decode($json['document']));
        break;
    }
        
    sleep(1);
}
