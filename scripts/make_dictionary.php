<?php

// Will generate a dictionary file from multiple file sources

$skipFile=fopen("entities_skip.log","w");
$errorFile=fopen("entities_error.log","w");

$stat=["PER"=>0,"ORG"=>0,"TOTAL"=>0];

$entities=["PER"=>[],"ORG"=>[]];
$entitiesLower=["PER"=>[],"ORG"=>[]];

$corola=[];

function loadCOROLA($fname){
    global $corola;

    echo "Loading COROLA freq from $fname\n";

    $fin=fopen($fname,"r");
    while(!feof($fin)){
        $line=fgets($fin);
        if($line===false)break;

        $line=trim($line);
        if(strlen($line)==0)continue;

        $data=explode("\t",$line);
        if(count($data)!=2)continue;
        $corola[$data[0]]=intval($data[1]);

    }
    fclose($fin);
}

function checkCOROLA($ent){ // ent must be lower
    global $corola;
    if(!isset($corola[$ent]) || $corola[$ent]<100)return true;
    return false;
}

function checkName($ent){
    if(preg_match("/[0-9,.;:'+=|\\\\]/",$ent))return false;
    return true;
}

function addEntity($type, $ent){
    global $entities,$entitiesLower,$skipFile,$errorFile;

    $el=mb_strtolower($ent);
    if(!isset($entitiesLower[$type][$el])){
        if(checkName($ent)){
            if(checkCOROLA($el)){
                $entitiesLower[$type][$el]=true;
                $entities[$type][]=$ent;
            }else{
                fwrite($skipFile,"$ent\n");
            }
        }else{
            fwrite($errorFile,"$ent\n");
        }
    }
}

function processJRCNames(){
    $fname="jrc-names.orig";
    echo "Processing $fname\n";
    $fin=fopen($fname,"r");
    while(!feof($fin)){
        $line=fgets($fin);
        if($line===false)break;

        $line=trim($line);
        if(strlen($line)==0)continue;

        $data=explode("\t",$line);
        if(count($data)!=4)continue;

        $type=$data[1];
        $enc=$data[2];
        $text=$data[3];
        $text=str_replace("+"," ",$text);

        if($enc!="u")continue;

        if($type=="P"){
            $type="PER";
            if(mb_strtoupper($text)==$text)continue; // ignore ORG marked as PER

            $words=explode(" ",trim(str_replace("  "," ",str_replace("-"," ",mb_strtolower($text)))));
            $wordsRev=array_flip($words);
            if(isset($wordsRev['din']))continue; // ignore PER names containing "din"
        }else if($type=="O"){
            $type="ORG"; 
            continue; // ignore ORG
        }else{
            echo "Unknown type $type\n";
            continue;
        }

        addEntity($type,$text);

    }

    fclose($fin);
}

function processICIA($type, $fname){
    echo "Processing $fname\n";
    $fin=fopen($fname,"r");
    while(!feof($fin)){
        $line=fgets($fin);
        if($line===false)break;

        $line=trim($line);
        if(strlen($line)==0)continue;

        addEntity($type,$line);

    }
    fclose($fin);
}

function processTSV($type, $fname){
    echo "Processing $fname\n";
    $fin=fopen($fname,"r");
    $n=0;
    while(!feof($fin)){
        $line=fgets($fin);
        if($line===false)break;

        $line=trim($line);
        if(strlen($line)==0)continue;

        $n++;
        if($n==0)continue;

        $data=explode("\t",$line);
        foreach($data as $text){
            if(strlen($text)==0)continue;
            if(strlen($text)<3)continue;

            addEntity($type,$text);
        }
    }
    fclose($fin);

}

loadCOROLA("corola_word_freq_gte10.tsv");
processJRCNames();
processICIA("PER","pernames-utf8-uniq.txt");
processICIA("PER","per-aditional.txt");
processICIA("ORG","orgnames-utf8-uniq.txt");
processTSV("PER","Anexa_3437170DictNumePrenume.tsv");

echo "Sorting\n";

$stat["PER"]=count($entities["PER"]);
$stat["ORG"]=count($entities["ORG"]);
$stat["TOTAL"]=$stat["PER"]+$stat["ORG"];
sort($entities["PER"]);
sort($entities["ORG"]);

echo "Writing output\n";
$fout=fopen("names_dictionary.dic","w");
foreach($entities["PER"] as $ent)fwrite($fout,"PER\t$ent\n");
foreach($entities["ORG"] as $ent)fwrite($fout,"ORG\t$ent\n");
fclose($fout);

fclose($skipFile);
fclose($errorFile);

var_dump($stat);

