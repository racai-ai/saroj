<?php

$url="http://127.0.0.1:8111";

$fnum=0;

function startsWith($haystack, $needle)
{

    if(is_array($needle)){
        foreach($needle as $n){
            if(startsWith($haystack,$n))return true;
        }
        return false;
    }

     $length = strlen($needle);
     return (substr($haystack, 0, $length) === $needle);
}

function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }

    return (substr($haystack, -$length) === $needle);
}


function changeFileExtension($fname,$newExt){
    $pos=strrpos($fname,".");
    if($pos===false)return "${fname}.${newExt}";
    return substr($fname,0,$pos).".".$newExt;
}

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

function sanitizeEntText($ent){
    $ent=str_replace("\n"," ",$ent);
    $ent=str_replace("\r"," ",$ent);
    $ent=str_replace("\t"," ",$ent);
    $ent=str_replace("<w:p>","",$ent);
    $ent=str_replace("<w:t>","",$ent);
    $ent=str_replace("</w:p>","",$ent);
    $ent=str_replace("</w:t>","",$ent);
    $ent=str_replace("&amp;","&",$ent);
    $ent=str_replace("&lt;","<",$ent);
    $ent=str_replace("&gt;",">",$ent);
    return $ent;
}

function adjustPosition($text, $pos){
    $t=substr($text,0,$pos);
    $ret=$pos;
    foreach( ["<w:p>","<w:t>","</w:p>","</w:t>","<d>","</d>"] as $s){
        $n=substr_count($t,$s);
        $ret-=strlen($s)*$n;
    }

    foreach( ["&amp;","&lt;","&gt;"] as $s){
        $n=substr_count($t,$s);
        $ret-=(strlen($s)-1)*$n; // one character remains
    }

    $l1=strlen($t);
    $l2=mb_strlen($t);

    $ret-=($l1-$l2);

    return $ret;
}

function pythonEscape($t){
    $r=$t;
    $r=str_replace("&","&amp;",$r);
    $r=str_replace("<","&lt;",$r);
    $r=str_replace(">","&gt;",$r);
    return $r;
}

function processAnn($ann,$fpathOutAnn,$fpathOutConllup, $fpathTxt){
    file_put_contents($fpathOutConllup,$ann);

    $fp=fopen($fpathTxt,"rb");
    $text="<d>";
    while(!feof($fp)){
        $line=fgets($fp);
        if($line===false)break;
        $line=pythonEscape($line);
        $text.="<w:p><w:t>$line</w:t></w:p>";
    }
    $text.="</d>";

    $current="O";
    $start=0;
    $end=0;
    $entId=1;
    $entities="";
    foreach(explode("\n",$ann) as $line){
        if(empty($line)){
            if($current!="O"){
                $entText=substr($text, $start, $end-$start);
                $entText=sanitizeEntText($entText);
                $start=adjustPosition($text,$start);
                $end=adjustPosition($text,$end);
                $entities.="T${entId}\t${current} ${start} $end\t${entText}\n";
                $entId++;
                $current="O";
                $start=0;
                $end=0;
            }
        }else {
            $data=explode("\t",$line);
            if(count($data)<5)continue;
            $token=$data[1];
            $ner=$data[count($data)-1];
            $tokStart=$data[count($data)-3];
            $tokEnd=$data[count($data)-2];

            if(strlen($ner)>2)$nertype=substr($ner,2);
            else $nertype=$ner;

            if($current!="O" && ($nertype=="O" || $nertype!=$current)){
                $entText=substr($text, $start, $end-$start);
                $entText=sanitizeEntText($entText);
                $start=adjustPosition($text,$start);
                $end=adjustPosition($text,$end);
                $entities.="T${entId}\t${current} ${start} $end\t${entText}\n";
                $entId++;
                $current="O";
                $start=0;
                $end=0;
            }

            if($current=="O" && $nertype!="O"){
                $current=$nertype;
                $start=$tokStart;
                $end=$tokEnd;
            }

            if($nertype!="O")$end=$tokEnd;

        }
    }
    if($current!="O"){
        $entText=substr($text, $start, $end-$start);
        $entText=sanitizeEntText($entText);
        $start=adjustPosition($text,$start);
        $end=adjustPosition($text,$end);
        $entities.="T${entId}\t${current} ${start} $end\t${entText}\n";
        $entId++;
        $current="O";
    }
    //file_put_contents($fpathOutTxt,$text);
    file_put_contents($fpathOutAnn,$entities);
}

function runSAROJ($dirTxt, $dirOut, $file){
    global $fnum;
    $fnum++;
    echo "   $fnum FILE: $dirTxt/$file\n";

    global $url;

    $fpathIn="$dirTxt/$file";
    $fpathOut="$dirOut/$file";
    $fpathOutAnn=changeFileExtension($fpathOut,"ann");
    $fpathOutConllup=changeFileExtension($fpathOut,"conllup");

    $docid=basename($fpathIn);
    $pos=strrpos($docid,"."); if($pos!==false)$docid=substr($docid,0,$pos);

    $caseid=$docid;
    $pos=strpos($caseid,"_"); if($pos!==false && $pos>0)$caseid=substr($caseid,0,$pos);

    $ret=sendData("$url/startAnonymization.php",
        [ "input" => json_encode([
          "caseid" => $caseid,
          "docid" => $docid,
          "type" => "txt",
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
                processAnn(base64_decode($json['outputann']), $fpathOutAnn, $fpathOutConllup, $fpathIn);
            }
            break;
        }

        if(!isset($json['status']) || $json['status']!=="OK")break;

        sleep(1);
    }

}

function runCorpus($dir,$runName){
    echo "CORPUS: $dir\n";
    if (!is_dir($dir)) die("Invalid folder [$dir]\n");
    $dirTxt="$dir/files";
    if (!is_dir($dirTxt)) die("Invalid folder [$dirTxt]\n");

    $dirOut="$dir/$runName";
    @mkdir($dirOut);

    if ($dh = opendir($dirTxt)) {
        while (($file = readdir($dh)) !== false) {
            $path="$dirTxt/$file";
            if(is_file($path) && endsWith($path,".txt")){
		$pathGold="$dir/gold_standoff/".changeFileExtension($file,"ann");
		if(!is_file($pathGold)){echo "SKIP: $dirTxt/$file\n"; continue; }
                runSAROJ($dirTxt, $dirOut, $file);
            }
        }
        closedir($dh);
    }

}

if(count($argv)!=3){
    die("run_saroj.php <corpus> <run_folder>\n");
}
//runCorpus("/home/ubuntu/vasile/test_corpora/documente_1","saroj_all");
#runCorpus("/home/ubuntu/vasile/corpora/DOC_R1","saroj_all");

echo "CORPUS=${argv[1]}\nRUN=${argv[2]}\n\n";

runCorpus($argv[1],$argv[2]);

?>