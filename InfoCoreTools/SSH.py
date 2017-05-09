# -*- coding: utf-8 -*-
import os
import logging

logger = logging.getLogger('root.InfoCoreTools.SSH')

#测试免密登录
#按照windows bat脚本提示，最终看到日期打印即为成功
def verifySSH(sshPath):
    if os.path.exists(sshPath):
        os.system(r'start {}\SSHBat\ssh.bat "{}"'.format(os.path.dirname(__file__), sshPath))

def verifySSH1(ip, username, sshPath):
    if os.path.exists(sshPath):
        output = os.popen(r'"{}" {}@{} date'.format(sshPath, username, ip))

def disableFCSwitchPort(switchIP, portNumber, sshPath):
    username = r'admin'
    if os.path.exists(sshPath):
        os.popen(r'"{}" {}@{} portdisable {}'.format(sshPath, username, switchIP, portNumber))

def enableFCSwitchPort(switchIP, portNumber, sshPath):
    username = r'admin'
    if os.path.exists(sshPath):
        os.popen(r'"{}" {}@{} portenable {}'.format(sshPath, username, switchIP, portNumber))