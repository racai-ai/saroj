<?php

// compare annotations REGEX/DICTIONARY/BERT

$f1=fopen("2_REGEX","r");
$f2=fopen("3_DICTIONARY","r");
$f3=fopen("4_BERT","r");

$lnum=0;
while(!feof($f1)){
    $lnum++;
    $s1=fgets($f1);
    $s2=fgets($f2);
    $s3=fgets($f3);

    $s1=trim($s1);
    $s2=trim($s2);
    $s3=trim($s3);

    $d1=explode("\t",$s1);
    $d2=explode("\t",$s2);
    $d3=explode("\t",$s3);

    if($d1[0]!=$d2[0] || $d1[0]!=$d3[0]){
	var_dump($s1);
	var_dump($s2);
	var_dump($s3);
	var_dump($lnum);
	die();
    }

    if(count($d1)==1)continue;

    if(strlen($d1[count($d1)-1])==0 || strlen($d2[count($d2)-1])==0 || strlen($d3[count($d3)-1])==0){
	var_dump($lnum);
	die();
    }
}

fclose($f1);
fclose($f2);
fclose($f3);
