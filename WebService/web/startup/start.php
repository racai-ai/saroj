<?php

set_time_limit(0);
ini_set('default_socket_timeout', 60*60);

require_once "../lib/lib.php";

$config=get_config();

echo "Starting modules\n";

foreach($config['modules'] as $mod){
	echo "   Running [$mod]\n";
	shell_exec(sprintf("/bin/bash -c %s >/dev/null 2>&1 &", escapeshellarg($mod)));
}

echo "All modules started\n";

echo "Creating folders and setting access rights\n";
@mkdir($TASK_DIR);
@mkdir($TASK_DIR_NEW);
@mkdir($TASK_DIR_NEW_PRIO);
@mkdir($TASK_DIR_DONE);
@mkdir($TASK_DIR_RUN);
@mkdir($MAP_DIR);
shell_exec("chown www-data:www-data ${TASK_DIR_NEW}");
shell_exec("chown www-data:www-data ${TASK_DIR_NEW_PRIO}");
shell_exec("chown www-data:www-data ${TASK_DIR_DONE}");
shell_exec("chown www-data:www-data ${TASK_DIR_RUN}");
shell_exec("chown www-data:www-data ${MAP_DIR}");
echo "Done\n";

function checkTasksPrio(){
        global $TASK_DIR_NEW_PRIO, $TASK_DIR_DONE;

	$dh = opendir($TASK_DIR_NEW_PRIO);
	while (($file = readdir($dh)) !== false) {
		$pathNew="${TASK_DIR_NEW_PRIO}${file}";
		$pathDone="${TASK_DIR_DONE}${file}";
		if(is_file($pathNew)){// && endsWith($pathNew,".task")){
			echo "Running PRIORITY task $file\n";
			
			runTask($pathNew, $pathDone);
			
			echo "Done\n";
		}
	}
	closedir($dh);
}


function checkTasks(){
        global $TASK_DIR_NEW, $TASK_DIR_DONE;

	$dh = opendir($TASK_DIR_NEW);
	checkTasksPrio();
	while (($file = readdir($dh)) !== false) {
		$pathNew="${TASK_DIR_NEW}${file}";
		$pathDone="${TASK_DIR_DONE}${file}";
		if(is_file($pathNew)){// && endsWith($pathNew,".task")){
			echo "Running task $file\n";
			
			runTask($pathNew, $pathDone);
			
			echo "Done\n";
			
			checkTasksPrio();
			
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
	file_put_contents($pathDocx,base64_decode($task['document']));

	$pathOutput="${TASK_DIR_RUN}output.docx";
	$pathOutputAnn="${TASK_DIR_RUN}output.ann";
	
	$pathCaseMap="${MAP_DIR}${task['caseid']}.map";
	
	$data=[
		"CASEID" => $task['caseid'],
		"DOCID" => $task['docid'],
		"DOCX" => $pathDocx,
		"CASEMAP" => $pathCaseMap,
		"OUTPUT" => $pathOutput,
		"OUTPUTANN" => $pathOutputAnn
	];
	
	foreach($config['anonymization'] as $step){
		$port=$step['port'];
		$stepData=[];
		foreach($step['args'] as $arg){
			$key=$arg['key'];
			$value=$arg['value'];
                        if(!is_array($value)){
			    if(!isset($data[$value])){
				$data[$value]="${TASK_DIR_RUN}${value}";
			    }
			    $stepData[$key]=$data[$value];
                        }else{
                            $stepData[$key]=[];
                            foreach($value as $v){
			        if(!isset($data[$v])){
				    $data[$v]="${TASK_DIR_RUN}${v}";
			        }
			        $stepData[$key][]=$data[$v];
                            }
                        }
		}
		
		$result=file_get_contents("http://127.0.0.1:$port/process?input=".urlencode(json_encode($stepData)));
                echo "Result on port $port: $result\n";
		if($result===false){
			$task['status']="ERROR";
			$task['message']="No answer on port $port";
			break;
		}
		$result=json_decode($result,true);
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
                        if(is_file($pathOutputAnn))$task['outputann']=base64_encode(file_get_contents($pathOutputAnn));
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
