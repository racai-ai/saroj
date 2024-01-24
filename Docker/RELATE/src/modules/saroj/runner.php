<?php

namespace Modules\saroj;

function sendData($url,$data){
    $ch = curl_init();

    $fields_string = http_build_query($data);
    curl_setopt_array($ch, array(
        CURLOPT_URL => $url,
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_MAXREDIRS => 10,
        CURLOPT_TIMEOUT => 60,
        //CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
        //CURLOPT_CUSTOMREQUEST => "POST",
        CURLOPT_POST => 1,
        CURLOPT_POSTFIELDS => $fields_string,
        CURLOPT_SSL_VERIFYHOST => 0,
        CURLOPT_SSL_VERIFYPEER => 0,
        //CURLOPT_VERBOSE => true
    ));


    $server_output = curl_exec($ch);

    curl_close ($ch);

    return $server_output;

}

function processAnn($corpus,$ann,$fpathOutAnn,$fpathOutConllup,$fpathOutTxt,$fpathOutMeta){
    file_put_contents($fpathOutConllup,$ann);
    file_put_contents($fpathOutMeta,json_encode([
        "name"=>basename($fpathOutTxt),
        "corpus" => $corpus->getName(),
        "type"=>"text",
        "desc"=>"Created by the SAROJ task",
        "created_by"=>"SAROJ",
        "created_date"=>strftime("%Y-%m-%d %H:%M:%S"),
    ]));

    $text="";
    $current="O";
    $start=0;
    $entId=1;
    $entities="";
    foreach(explode("\n",$ann) as $line){
        if(empty($line)){
            if($current!="O"){
                $entText=mb_substr($text,$start);
                $pos=$start+mb_strlen($entText)-1;
                $entities.="T${entId}\t${current} ${start} $pos\t${entText}\n";
                $entId++;
                $current="O";
            }
            $text.="\n";
        }else {
            $data=explode("\t",$line);
            if(count($data)<5)continue;
            $token=$data[1];
            $ner=$data[count($data)-1];

            if(strlen($ner)>2)$nertype=substr($ner,2);
            else $nertype=$ner;

            if($current!="O" && ($nertype=="O" || $nertype!=$current)){
                $entText=mb_substr($text,$start);
                $pos=$start+mb_strlen($entText)-1;
                $entities.="T${entId}\t${current} ${start} $pos\t${entText}\n";
                $entId++;
                $current="O";
            }

            if($current=="O" && $nertype!="O"){
                $current=$nertype;
                $start=mb_strlen($text);
            }

            $text.=$token." ";
        }
    }
    if($current!="O"){
        $entText=mb_substr($text,$start);
        $pos=$start+mb_strlen($entText)-1;
        $entities.="T${entId}\t${current} ${start} $pos\t${entText}\n";
        $entId++;
        $current="O";
    }
    file_put_contents($fpathOutTxt,$text);
    file_put_contents($fpathOutAnn,$entities);
}

function runSAROJ($corpus,$fpathIn,$fpathOut,$fpathOutAnn,$fpathOutConllup,$fpathOutTxt,$fpathOutMeta){
    global $settings;
    $url=$settings->get("saroj.url");

    $docid=basename($fpathIn);
    $pos=strrpos($docid,"."); if($pos!==false)$docid=substr($docid,0,$pos);

    $caseid=$docid;
    $pos=strpos($caseid,"_"); if($pos!==false && $pos>0)$caseid=substr($caseid,0,$pos);

    $ret=sendData("$url/startAnonymization.php",
        [ "input" => json_encode([
          "caseid" => $caseid,
          "docid" => $docid,
          "document" => base64_encode(file_get_contents($fpathIn))
    ])]);

    $data=json_decode($ret,true);
    $id=$data['id'];

    while(true){
        $ret=file_get_contents("$url/getResult.php?input=".urlencode(json_encode(["id"=>$id])));
        $json=json_decode($ret,true);
        if(
            isset($json['status']) && $json['status']=="OK" &&
            isset($json['result']) && $json['result']=="DONE" &&
            isset($json['document'])
        ){
            file_put_contents($fpathOut,base64_decode($json['document']));
            if(isset($json['outputann'])){
                processAnn($corpus,base64_decode($json['outputann']), $fpathOutAnn, $fpathOutConllup, $fpathOutTxt, $fpathOutMeta);
            }
            break;
        }

        if(!isset($json['status']) || $json['status']!=="OK")break;

        sleep(1);
    }

}

function runner($runner,$settings,$corpus,$taskDesc,$data,$contentIn,$fnameOut){
    $path=$corpus->getFolderPath()."/standoff/";
    $pathConllup=$corpus->getFolderPath()."/basic_tagging/";
    $pathTxt=$corpus->getFolderPath()."/files/";
    $pathMeta=$corpus->getFolderPath()."/meta/";

    $fnameOutAnn=changeFileExtension($fnameOut,"ann");
    $fnameOutTxt=changeFileExtension($fnameOut,"txt");
    $fnameOutMeta=$fnameOutTxt.".meta";
    $fnameOutConllup=changeFileExtension($fnameOut,"conllup");
    $fnameOut="SAROJ_".changeFileExtension($fnameOut,"docx");

    $finalFileAnn=$path.$fnameOutAnn;
    $finalFileTxt=$pathTxt.$fnameOutTxt;
    $finalFileMeta=$pathMeta.$fnameOutMeta;
    $finalFileConllup=$pathConllup.$fnameOutAnn;
    $finalFile=$path.$fnameOut;

    echo "Destination for SAROJ $finalFile , $finalFileAnn\n";
    @mkdir($path);
    @mkdir($pathConllup);
    @mkdir($pathTxt);
    @mkdir($pathMeta);

    runSAROJ($corpus,$data['fpath'],$finalFile,$finalFileAnn,$finalFileConllup,$finalFileTxt,$finalFileMeta);
    
    file_put_contents($corpus->getFolderPath()."/changed_standoff.json",json_encode(["changed"=>time()]));            
    file_put_contents($corpus->getFolderPath()."/changed_files.json",json_encode(["changed"=>time()]));            
    file_put_contents($corpus->getFolderPath()."/changed_basictagging.json",json_encode(["changed"=>time()]));            
    file_put_contents($corpus->getFolderPath()."/changed_annotated.json",json_encode(["changed"=>time()]));            
}


?>