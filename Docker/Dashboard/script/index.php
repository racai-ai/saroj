<?php

$users=[
    "DOC_1"=>"",
    "DOC_2"=>"",
    "DOC_3"=>"",
    "DOC_4"=>"",
    "DOC_5"=>"",
    "DOC_6"=>"",
    "DOC_7"=>"",
    "DOC_8"=>"",
    "DOC_9"=>"",
    "DOC_10"=>"",
    "DOC_11"=>"",
    "DOC_12"=>"",
    "DOC_13"=>"",
    "DOC_14"=>"",
    "DOC_15"=>"",
    "DOC_16"=>"",
    "DOC_17"=>"",
    "DOC_18"=>"",
    "DOC_19"=>"",
    "DOC_20"=>"",
    "DOC_21"=>"",
    "DOC_22"=>"",
    "DOC_23"=>"",
    "DOC_24"=>"",
    "DOC_25"=>"",
    "DOC_26"=>"",
    "DOC_27"=>"",
    "DOC_28"=>"",
    "DOC_29"=>"",
    "DOC_30"=>"",
    "DOC_31"=>"",
    "DOC_32"=>"",
    "DOC_33"=>"",
    "DOC_34"=>"",
    "DOC_R1"=>"",
    "DOC_R2"=>""
];

?>
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Dashboard</title>

    <style>
      #loader {
        transition: all 0.3s ease-in-out;
        opacity: 1;
        visibility: visible;
        position: fixed;
        height: 100vh;
        width: 100%;
        background: #fff;
        z-index: 90000;
      }

      #loader.fadeOut {
        opacity: 0;
        visibility: hidden;
      }

      .spinner {
        width: 40px;
        height: 40px;
        position: absolute;
        top: calc(50% - 20px);
        left: calc(50% - 20px);
        background-color: #333;
        border-radius: 100%;
        -webkit-animation: sk-scaleout 1.0s infinite ease-in-out;
        animation: sk-scaleout 1.0s infinite ease-in-out;
      }

      @-webkit-keyframes sk-scaleout {
        0% { -webkit-transform: scale(0) }
        100% {
          -webkit-transform: scale(1.0);
          opacity: 0;
        }
      }

      @keyframes sk-scaleout {
        0% {
          -webkit-transform: scale(0);
          transform: scale(0);
        } 100% {
          -webkit-transform: scale(1.0);
          transform: scale(1.0);
          opacity: 0;
        }
      }
    </style>
  </head>
  <body class="app">
    <!-- @TOC -->
    <!-- =================================================== -->
    <!--
      + @Page Loader
      + @App Content
          - #Left Sidebar
              > $Sidebar Header
              > $Sidebar Menu

          - #Main
              > $Topbar
              > $App Screen Content
    -->

    <!-- @Page Loader -->
    <!-- =================================================== -->
    <div id='loader'>
      <div class="spinner"></div>
    </div>

    <script>
      window.addEventListener('load', function load() {
        const loader = document.getElementById('loader');
        setTimeout(function() {
          loader.classList.add('fadeOut');
        }, 300);
      });
    </script>

    <!-- @App Content -->
    <!-- =================================================== -->
    <div>
      <!-- #Left Sidebar ==================== -->
      <div class="sidebar">
        <div class="sidebar-inner">
          <!-- ### $Sidebar Header ### -->
          <div class="sidebar-logo">
            <div class="peers ai-c fxw-nw">
              <div class="peer peer-greed">
                <a class="sidebar-link td-n" href="index.html">
                  <div class="peers ai-c fxw-nw">
                    <div class="peer">
                      <div class="logo">
                        <img src="assets/static/images/logo.png" alt="">
                      </div>
                    </div>
                    <div class="peer peer-greed">
                      <h5 class="lh-1 mB-0 logo-text">SAROJ</h5>
                    </div>
                  </div>
                </a>
              </div>
              <div class="peer">
                <div class="mobile-toggle sidebar-toggle">
                  <a href="" class="td-n">
                    <i class="ti-arrow-circle-left"></i>
                  </a>
                </div>
              </div>
            </div>
          </div>

          <!-- ### $Sidebar Menu ### -->
          <ul class="sidebar-menu scrollable pos-r">
            <li class="nav-item mT-30 actived">
              <a class="sidebar-link" href="index.html">
                <span class="icon-holder">
                  <i class="c-blue-500 ti-home"></i>
                </span>
                <span class="title">Dashboard</span>
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- #Main ============================ -->
      <div class="page-container">
        <!-- ### $Topbar ### -->
        <div class="header navbar">
          <div class="header-container">
            <ul class="nav-left">
              <li>
                <a id='sidebar-toggle' class="sidebar-toggle" href="javascript:void(0);">
                  <i class="ti-menu"></i>
                </a>
              </li>
            </ul>
            <!--<ul class="nav-right">
            </ul>-->
          </div>
        </div>

        <!-- ### $App Screen Content ### -->
        <main class='main-content bgc-grey-100'>
          <div id='mainContent'>
            <div class="row gap-20 masonry pos-r">
              <div class="masonry-sizer col-md-6"></div>
              <div class="masonry-item  w-100">

<?php foreach($users as $uid=>$data){ 

$totalFiles=count(glob("/site/DB/corpora/$uid/files/*.txt"));

$nGold=0;
$nGoldEntities=0;
foreach(glob("/site/DB/corpora/$uid/gold_standoff/*.ann") as $fname){
    $nGold++;
    $nge=count(explode("\n",file_get_contents($fname)));
    if($nge>0)$nge--;
    $nGoldEntities+=$nge;
}
$nFiles=0;
$nFileEntities=0;
foreach(glob("/site/DB/corpora/$uid/standoff/*.ann") as $fname){
    $nFiles++;
    $nfe=count(explode("\n",file_get_contents($fname)));
    if($nfe>0)$nfe--;
    $nFileEntities+=$nfe;
}

$nGoldNumber=$nGold;

$nGold=intval($nGold*100/$totalFiles);

$color="#f20c0c";
if($nGold>25)$color="#f59042";
if($nGold>50)$color="#f2e60c";
if($nGold>75)$color="#1ff20c";

?>
                <div class="row gap-20">

                    <div class="col-md-3">
                      <div class="peer bd bgc-white p-10">
                        <div class="easy-pie-chart" data-size='80' data-percent="<?php echo $nGold; ?>" data-bar-color="<?php echo $color; ?>">
                          <span></span>
                        </div>
                        <h6 class="fsz-sm" style="text-align:center"><?php echo mb_strtoupper($uid); ?></h6>
                      </div>
                  </div>

                  <div class='col-md-6'>
                    <div class="layers bd bgc-white p-20">
                      <div class="layer w-100 mB-10">
                        <h6 class="lh-1">Gold Files: <?php echo $nGoldNumber; ?></h6>
                        <h6 class="lh-1">Gold Entities: <?php echo $nGoldEntities;?></h6>
                        <h6 class="lh-1">Annotated Files: <?php echo $nFiles;?></h6>
                        <h6 class="lh-1">Annotated Entities: <?php echo $nFileEntities;?></h6>
                      </div>
                    </div>
                  </div>

                </div>
<?php } ?>
              </div>
            </div>
          </div>
        </main>

        <!-- ### $App Screen Footer ### -->
        <footer class="bdT ta-c p-30 lh-0 fsz-sm c-grey-600">
          <span>.</span>
        </footer>
      </div>
    </div>
	<script type="text/javascript" src="./vendor.js"></script><script type="text/javascript" src="./bundle.js"></script>
  </body>
</html>
