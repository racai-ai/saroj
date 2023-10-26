<?php

set_time_limit(0);

require_once "../lib/lib.php";

$config=get_config();

echo "Starting modules\n";

foreach($config['modules'] as $mod){
	echo "   Running [$mod]\n";
	exec(sprintf("%s &", $mod));
}

echo "All modules started\n";

echo "Creating folders\n";
@mkdir($TASK_DIR);
@mkdir($TASK_DIR_NEW);
@mkdir($TASK_DIR_OLD);
@mkdir($TASK_DIR_RUN);
@mkdir($MAP_DIR);
echo "Done\n";

function checkTasks(){
	$dh = opendir($TASK_DIR_NEW);
	while (($file = readdir($dh)) !== false) {
		$pathNew="${TASK_DIR_NEW}${file}";
		$pathDone="${TASK_DIR_OLD}${file}";
		if(is_file($pathNew) && endsWith($pathNew,".task")){
			echo "Running task $file\n";
			
			runTask($pathNew, $pathDone);
			
			echo "Done\n";
		}
	}
	closedir($dh);
}

function runTask($pathNew, $pathDone){
	global $TASK_DIR_RUN, $MAP_DIR, $config;
	
	if(is_file($pathDone) && filesize($pathDone)>0){
		echo "Was already executed; remove\n";
		@unlink($pathNew);
		return ;
	}
	
	$task=json_decode(file_get_contents($pathNew),true);
	if(!is_array($task) || !isset($task["caseid"]) || !isset($task["docid"]) || !isset($task["document"]) || !isset($task["status"])){
		echo "Invalid task file\n";
		file_put_contents($pathDone,json_encode(["status"=>"ERROR","message"=>"Invalid task file"]));
		@unlink($pathNew);
		return ;
	}
	
	$task['status']="RUNNING";
	$task['version']=$config['version'];
	file_put_contents($pathNew,json_encode($task));
	
	$pathDocx="${TASK_DIR_RUN}input.docx";
	file_put_contents($pathDocx,$task['document']);

	$pathOutput="${TASK_DIR_RUN}output.docx";
	
	$pathCaseMap="${MAP_DIR}${task['caseid']}.map";
	
	$data=[
		"CASEID" => $task['caseid'],
		"DOCID" => $task['docid'],
		"DOCX" => $pathDocx,
		"CASEMAP" => $pathCaseMap,
		"OUTPUT" => $pathOutput
	];
	
	foreach($config['anonymization'] as $step){
		$port=$step['port'];
		$stepData=[];
		foreach($step['args'] as $arg){
			$key=$arg['key'];
			$value=$arg['value'];
			if(!isset($data[$value])){
				$data[$value]="${TASK_DIR_RUN}${value}";
			}
			$stepData[$key]=$data[$value];
		}
		
		$result=file_get_contents("http://127.0.0.1:$port/process?input=".url_encode(json_encode($stepData)));
		if($result===false){
			$task['status']="ERROR";
			$task['message']="No answer on port $port";
			break;
		}
		$result=json_decode($result);
		if(!is_array($result) || !isset($result['status'])){
			$task['status']="ERROR";
			$task['message']="Invalid JSON on port $port";
			break;
		}			
		
		if($result['status']!=="OK"){
			$task['status']="ERROR";
			$task['message']="Error on port $port: ".$result['message'];
			break;
		}
		
	}
	
	if($task['status']!=="ERROR"){
		if(!is_file($pathOutput)){
			$task['status']="ERROR";
			$task['message']="Output file was not generated";
		}else{
			$task['output']=base64_encode(file_get_contents($pathOutput));
			$task['status']="DONE";
		}
	}
	
	file_put_contents($pathDone, json_encode($task));
	@unlink($pathNew);
}

echo "\n\nExecuting tasks....\n";
while(true){
	sleep(1);
	checkTasks();
}
