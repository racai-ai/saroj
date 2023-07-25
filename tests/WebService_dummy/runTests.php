<?php

require_once "../lib/lib.php";

echo "Running Dummy Web Service tests\n";

global $wsURL;
$wsURL=getenv('WSURL');
if($wsURL===false){
	die("ERROR: Environment variable WSURL is not set\n");
}


$dh = opendir(".");
while (($dir = readdir($dh)) !== false) {
	if(is_dir($dir) && is_file("$dir/test.php")){
		echo "    [$dir] .... ";
		{
			include "$dir/test.php";
		}
		echo "OK\n";
    }
}
closedir($dh);
