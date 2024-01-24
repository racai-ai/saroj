<?php

function get_config(){

	if(!is_file("/data/config.json")){
		die(json_encode(["status"=>"ERROR", "message"=>"E990 config.json not found"]));
	}
	
	$data=@json_decode(@file_get_contents("/data/config.json"),true);
	if(!is_array($data) || !isset($data['version']) || !isset($data['modules']) || !isset($data['anonymization'])){
		die(json_encode(["status"=>"ERROR", "message"=>"E991 Invalid config.json file"]));
	}
		
	return $data;

}
