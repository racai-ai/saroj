<?php

$users=['coref1','coref2','coref3','coref4','coref5','coref6','coref7'];

function getPath($user,$folder){
    return "/data/RELATE/internal/$user/DB/corpora/COREF1/gold_standoff/$folder";
}
function getPathT($user,$folder){
    return "/data/RELATE/internal/$user/DB/corpora/COREF1/files/$folder";
}

function cmp_clusters($a,$b){
    $ma=$a[0][0];
    foreach($a as $ac)if($ac[0]<$ma)$ma=$ac[0];

    $mb=$b[0][0];
    foreach($b as $bc)if($bc[0]<$mb)$mb=$bc[0];

    return ($ma<$mb)?-1:1;
}

function getClusters($ann){
    $clusters=[];
    foreach(explode("\n",file_get_contents($ann)) as $line){
        $line=trim($line);
        if(empty($line))continue;

        $data=explode("\t",$line);
        if(count($data)!=3)continue;
        $data[1]=explode(" ",$data[1]);
        if(count($data[1])!=3)continue;

        if(!isset($clusters[$data[1][0]]))$clusters[$data[1][0]]=[];
        $clusters[$data[1][0]][]=[intval($data[1][1]),intval($data[1][2])];
    }

    $clusters=array_values($clusters);
    usort($clusters,"cmp_clusters");

    $clusters_s=[];
    foreach($clusters as $k=>$c){
        $nc=[];
        $m=-1;
        foreach($c as $cc){
            $nc["${cc[0]}_${cc[1]}"]=true;
            if($m==-1 || $m<$cc[0])$m=$cc[0];
        }
        //$clusters_s[$k]=array_keys($nc);
        $clusters_s[strval($m)]=array_keys($nc);
    }

    return $clusters_s;
}

//var_export(getClusters(getPath("coref2","62021CC0156_001.ann")));

function agreement($u1,$u2){
    $agg=[
        'files1'=>0,
        'files2'=>0,
        'files_common'=>0,
        'filesr1'=>0,
        'filesr2'=>0,
        'filesr_common'=>0,
        'clusters_1'=>0,
        'clusters_2'=>0,
        'clusters_common'=>0,
        'clusters_common_i'=>0,
        'clusters_common_w1'=>0,
        'clusters_common_w2'=>0,
        'clusters_common_wc'=>0,
    ];

    $agg['files2']=count(glob(getPath($u2,"*.ann")));

    $agg['filesr1']=count(glob(getPathT($u1,"*.txt")));
    $agg['filesr2']=count(glob(getPathT($u2,"*.txt")));
    $agg['filesr_common']=count(array_intersect(
        array_map("basename",glob(getPathT($u1,"*.txt"))),
        array_map("basename",glob(getPathT($u2,"*.txt")))
    ));

    foreach(glob(getPath($u1,"*.ann")) as $fpath1){
        $agg['files1']++;
        $fpath2=getPath($u2,basename($fpath1));
        if(!is_file($fpath2))continue;
        $agg['files_common']++;

        $c1=getClusters($fpath1);
        $c2=getClusters($fpath2);

        $agg['clusters_1']+=count($c1);
        $agg['clusters_2']+=count($c2);

        foreach($c1 as $k=>$c){
            if(isset($c2[$k])){
                $agg['clusters_common']++;
                $agg['clusters_common_w1']+=count($c);
                $agg['clusters_common_w2']+=count($c2[$k]);
                $agg['clusters_common_wc']+=count(array_intersect($c,$c2[$k]));
                if(count($c)==count($c2[$k]) && count(array_intersect($c,$c2[$k]))==count($c))$agg['clusters_common_i']++;
            }
        }
    }
    return $agg;
}

//var_export(agreement("coref1","coref2"));

echo sprintf("%20s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s%5s\n",
    "U1 -> U2","FT1","FT2","FTC","F1","F2","FC","C1","C2","CC","CCI","CCW1","CCW2","CCWC");


for($i=0;$i<count($users);$i++){
    for($j=$i+1;$j<count($users);$j++){
        if($i==$j)continue;
        $agg=agreement($users[$i],$users[$j]);
        //if($agg['files_common']==0)continue;
        if($agg['filesr_common']==0)continue;

        echo sprintf("%20s%5d%5d%5d%5d%5d%5d%5d%5d%5d%5d%5d%5d%5d\n",
            "${users[$i]} -> ${users[$j]}",
            $agg['filesr1'],
            $agg['filesr2'],
            $agg['filesr_common'],
            $agg['files1'],
            $agg['files2'],
            $agg['files_common'],
            $agg['clusters_1'],
            $agg['clusters_2'],
            $agg['clusters_common'],
            $agg['clusters_common_i'],
            $agg['clusters_common_w1'],
            $agg['clusters_common_w2'],
            $agg['clusters_common_wc']);
    }
}

