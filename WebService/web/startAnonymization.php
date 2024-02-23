<?php

require_once "lib/lib.php";

$in=get_input(["caseid","docid","document"],["type"=>"docx"]);

$in['type']=strtolower($in['type']);
if($in['type']!="txt" && $in['type']!="docx" && $in['type']!="html")
	die(json_encode(["status"=>"ERROR","message"=>"E007 Invalid type"]));

if(isset($in['priority']) && $in['priority']==1){
	$fname=tempnam($TASK_DIR_NEW_PRIO,uniqid());
	if($fname===false)
		die(json_encode(["status"=>"ERROR","message"=>"E004 Error creating task"]));

	if(!startsWith($fname,$TASK_DIR_NEW_PRIO))
		die(json_encode(["status"=>"ERROR","message"=>"E005 Error creating task"]));
	$taskid=substr($fname,strlen($TASK_DIR_NEW_PRIO));
}else{
	$fname=tempnam($TASK_DIR_NEW,uniqid());
	if($fname===false)
		die(json_encode(["status"=>"ERROR","message"=>"E004 Error creating task"]));

	if(!startsWith($fname,$TASK_DIR_NEW))
		die(json_encode(["status"=>"ERROR","message"=>"E005 Error creating task"]));
	$taskid=substr($fname,strlen($TASK_DIR_NEW));
}

$in['status']="SCHEDULED";
$in['message']="";

if(file_put_contents($fname,json_encode($in))===false)
	die(json_encode(["status"=>"ERROR","message"=>"E006 Error creating task"]));
	
echo json_encode(["status"=>"OK","id"=>$taskid]);

