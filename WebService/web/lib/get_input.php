<?php

function get_input($keys,$opt=[]){
	if(!isset($_REQUEST['input'])){
		die('{"status":"ERROR", "message":"E001 No input provided"}');
	}

	$input=json_decode($_REQUEST['input'],true);
	if($input===null){
		die('{"status":"ERROR", "message":"E002 Invalid input JSON provided"}');
	}
	
	foreach($keys as $k){
		if(!isset($input[$k])){
			die('{"status":"ERROR", "message":"E003 Missing key in input JSON ['.$k.']"}');
		}
	}

	foreach($opt as $k=>$v){
		if(!isset($input[$k])){
			$input[$k]=$v;
		}
	}
	
	return $input;
}
