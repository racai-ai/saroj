<?php

function wsCall($method,$data){
	global $DEBUG, $wsURL;
	
    set_time_limit(80);

    $ch = curl_init();

	$url=$wsURL.$method;
    
    curl_setopt_array($ch, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 60,
        CURLOPT_POST => 1,
        CURLOPT_POSTFIELDS => ["input"=>json_encode($data)],
        CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_SSL_VERIFYPEER => 0,
        CURLOPT_VERBOSE => $DEBUG
    ));
    
    
    $server_output = curl_exec($ch);
    
    curl_close ($ch);
    
    if($DEBUG)var_dump($server_output);
    
    
    return json_decode($server_output,true);

}
