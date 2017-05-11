# -*- coding: utf-8 -*-
import os
import sys
import logging

logger = logging.getLogger('root.InfoCoreTools.IPMI')

#设置IPMItool.exe的路径
IPMITool = r'{}\InfoCoreTools\bmc\ipmitool.exe'.format(os.path.dirname(os.path.abspath(sys.argv[0])))

#使用IPMI远程开机，调用ipmitool.exe实现
def powerOn(ip, username, password):
    if os.path.exists(IPMITool):
        logger.debug(r'ipmitool:打开电源 {}'.format(ip))
        output = os.popen(r'{} -I lanplus -H {} -U {} -P {} chassis power on 2>nul'.format(IPMITool,
                                                                                     ip,
                                                                                     username,
                                                                                     password))
        return output.read()
    else:
        logger.debug(r'IPMItool.exe未找到，确认路径{}是否正确'.format(IPMITool))
        sys.exit()

#使用IPMI远程关机，调用ipmitool.exe实现
def powerOff(ip, username, password):
    if os.path.exists(IPMITool):
        logger.debug(r'ipmitool:关闭电源 {}'.format(ip))
        output = os.popen(r'{} -I lanplus -H {} -U {} -P {} chassis power off 2>nul'.format(IPMITool,
                                                                                      ip,
                                                                                      username,
                                                                                      password))
        return output.read()
    else:
        logger.debug(r'IPMItool.exe未找到，确认路径{}是否正确'.format(IPMITool))
        sys.exit()

#查询计算机的电源状态，调用ipmitool.exe实现
def powerStatus(ip, username, password):
    if os.path.exists(IPMITool):
        #logger.debug(r'ipmitool:查询电源状态 {}'.format(ip))
        output = os.popen(r'{} -I lanplus -H {} -U {} -P {} chassis power status 2>nul'.format(IPMITool,
                                                                                         ip,
                                                                                         username,
                                                                                         password))
        state = output.read().strip('\n')
        if state == 'Chassis Power is on':
            return 1
        elif state == 'Chassis Power is off':
            return 0
        else:
            return -1
    else:
        logger.debug(r'IPMItool.exe未找到，确认路径{}是否正确'.format(IPMITool))
        sys.exit()

powerStatus('192.168.9.84','USERID','PASSW0RD')