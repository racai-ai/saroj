<?php

require_once "../lib/lib.php";

echo "Running Dummy Web Service tests\n";

if(!isset($_ENV['WSURL'])){
	die("ERROR: Environment variable WSURL is not set\n");
}

global $wsURL;
$wsURL=$_ENV['WSURL'];

$dh = opendir(".");
while (($file = readdir($dh)) !== false) {
	if(is_dir($file) && is_file("$file/test.php")){
		echo "    [$dir] .... ";
		{
			include "$dir/test.php";
		}
		echo "OK\n";
    }
}
closedir($dh);
