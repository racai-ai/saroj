<?php

require_once "lib/lib.php";

$config=get_config();

echo json_encode(["status"=>"OK", "version" => $config['version']]);
