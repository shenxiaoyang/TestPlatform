echo off

echo ��ӭʹ�ü��ssh���ܽű�
echo �������Are you sure you want to continue connecting (yes/no)? ������yes
echo ���������Ҫ�������룬��Կ��δ�ϴ����������ϣ������ϴ�����������
echo ʹ��ctrl+z�˳��ű�

rem 1%���ssh2.exe������·���Բ�����ʽ����ű�
:start
set /p ip=������SSH��������IP��ַ:
set /p username=������SSH���������û���:
%1 %username%@%ip% date
goto start
