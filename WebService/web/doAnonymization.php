<?php

require_once "lib/lib.php";

$in=get_input(["caseid","docid","document"]);
$in['priority']=1;

$data=@file_get_contents("http://127.0.0.1:80/startAnonymization?input=".urlencode(json_encode($in)));
if($data===false){
	die(json_encode(["status"=>"ERROR", "message"=>"E300 Error scheduling task"]));
}

$dataJson=json_decode($data,true);
if(!is_array($dataJson) || !isset($dataJson['status'])){
	die(json_encode(["status"=>"ERROR", "message"=>"E301 Error scheduling task"]));
}
	
if($dataJson['status']!=="OK"){
	die($data);
}

if(!isset($dataJson['id'])){
	die(json_encode(["status"=>"ERROR", "message"=>"E302 Error scheduling task"]));
}

$taskId=$dataJson['id'];
while(true){
	$data=@file_get_contents("http://127.0.0.1:80/getResult?input=".urlencode(json_encode(["id"=>$taskId])));
	if($data===false){
		die(json_encode(["status"=>"ERROR", "message"=>"E303 Error retrieving result"]));
	}
	
	$dataJson=json_decode($data,true);
	if(!is_array($dataJson) || !isset($dataJson['status'])){
		die(json_encode(["status"=>"ERROR", "message"=>"E304 Error retrieving result"]));
	}
	
	if($dataJson['status']==="ERROR" || $dataJson['status']==="OK"){
		die($data);
	}
	
	sleep(1);
}
