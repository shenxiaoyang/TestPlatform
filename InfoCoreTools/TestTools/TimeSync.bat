set "ipaddr=192.168.23.88"
set "username=test001"
set "password=sxysxy3819"


net use \\%ipaddr% %password% /user:%username%

net time \\%ipaddr% /set /y

net use \\%ipaddr% /d /y

pause