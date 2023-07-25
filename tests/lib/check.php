<?php

function checkString($real,$expected){
	if($real!==$expected){
		die("ERROR: Expecting [$expected], got [$real]\n");
	}
	return true;
}

function checkJSON($real, $expected){
	foreach($expected as $k=>$v){
		if(!is_array($real) || !isset($real[$k])){
			die("ERROR: JSON response is missing key [$k]\n");
		}
		checkString($real[$k],$v);
	}
	return true;
}
