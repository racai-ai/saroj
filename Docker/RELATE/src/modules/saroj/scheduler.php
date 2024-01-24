<?php

namespace Modules\saroj;

function schedule($settings,$corpus,$task_name,$tdata){
   scheduleFolder($corpus,"standoff",$task_name,"docx",".docx","SAROJ_");
}

?>