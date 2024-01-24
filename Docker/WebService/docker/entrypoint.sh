#!/bin/sh

cd /site/startup ; php start.php 2>&1 | /usr/bin/rotatelogs -l /var/log/saroj_runner-%Y-%m-%d.log 86400 &

cd /

/usr/sbin/apachectl -D FOREGROUND
