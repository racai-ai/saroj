<?php

checkJSON(wsCall("getVersion.php", []), ["status"=>"OK", "message"=>"", "version"=>"DUMMY_WEBSERVICE"]);
