echo off

echo 欢迎使用检测ssh免密脚本
echo 如果出现Are you sure you want to continue connecting (yes/no)? 则输入yes
echo 如果出现需要输入密码，则公钥还未上传到服务器上，请先上传到服务器上
echo 使用ctrl+z退出脚本

rem 1%请把ssh2.exe的完整路径以参数形式传入脚本
:start
set /p ip=请输入SSH服务器的IP地址:
set /p username=请输入SSH服务器的用户名:
%1 %username%@%ip% date
goto start
