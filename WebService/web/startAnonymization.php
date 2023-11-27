<?php

require_once "lib/lib.php";

$in=get_input(["caseid","docid","document"]);

$fname=tempnam($TASK_DIR_NEW,uniqid());
if($fname===false)
	die(json_encode(["status"=>"ERROR","message"=>"E004 Error creating task"]));

if(!startsWith($fname,$TASK_DIR_NEW))
	die(json_encode(["status"=>"ERROR","message"=>"E005 Error creating task"]));

$in['status']="SCHEDULED";
$in['message']="";

if(file_put_contents($fname,json_encode($in))===false)
	die(json_encode(["status"=>"ERROR","message"=>"E006 Error creating task"]));
	
echo json_encode(["status"=>"OK","id"=>substr($fname,strlen($TASK_DIR_NEW))]);

