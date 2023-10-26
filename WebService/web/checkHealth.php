<?php

require_once "lib/lib.php";

$config=get_config();

$message="";
$status="OK";
foreach($config['anonymization'] as $mod){
	$data=file_get_contents("http://127.0.0.1:".$mod['port']."/check_health");
	$data=@json_decode($data,true);
	if(!is_array($data) || !isset($data['status']) || !isset($data['message'])){
		$status="ERROR"; 
		$message.="E101 Invalid JSON on port ".$mod['port']."\n";
		break;
	}
	
	if($data['status']!="OK"){
		$status="ERROR";
		$message.="E100 Error on port ".$mod['port'].": ".$data['message']."\n";
		break;
	}
	
	if(strlen($data['message'])>0)$message.=$data['message']."\n";
}

echo json_encode(["status"=>$status,"message"=>$message, "version"=>$config['version']]);
