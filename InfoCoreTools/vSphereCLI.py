# -*- coding: utf-8 -*-

import os
import sys
import logging
import re

logger = logging.getLogger('root.InfoCoreTools.vSphereCLI')
vSphereCLI = r'C:\Program Files (x86)\VMware\VMware vSphere CLI\bin\vmware-cmd.pl'
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')

def startVirtualMachineSoft(esxiIP, esxiUsername, esxiPassword, vmName):
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    if zhPattern.findall(vmx):
        logger.error(r'不支持中文名称的虚拟机')
        exit(1)
    cmd = r'{} {}'.format(vmx, r'start soft')
    result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
    logger.debug(r'{} {}'.format(vmx.split('/')[-1],result))

def startVirtualMachineHard(esxiIP, esxiUsername, esxiPassword, vmName):
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    if zhPattern.findall(vmx):
        logger.error(r'不支持中文名称的虚拟机')
        exit(1)
    cmd = r'{} {}'.format(vmx, r'start hard')
    result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
    logger.debug(r'{} {}'.format(vmx.split('/')[-1],result))

def stopVirtualMachineSoft(esxiIP, esxiUsername, esxiPassword, vmName):
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    if zhPattern.findall(vmx):
        logger.error(r'不支持中文名称的虚拟机')
        exit(1)
    cmd = r'{} {}'.format(vmx, r'stop soft')
    result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
    logger.debug(r'{} {}'.format(vmx.split('/')[-1],result))

def stopVirtualMachineHard(esxiIP, esxiUsername, esxiPassword, vmName):
    vmx = getVmxByVirtualMachineName(esxiIP, esxiUsername, esxiPassword, vmName)
    if zhPattern.findall(vmx):
        logger.error(r'不支持中文名称的虚拟机')
        exit(1)
    cmd = r'{} {}'.format(vmx, r'stop hard')
    result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd)
    logger.debug(r'{} {}'.format(vmx.split('/')[-1],result))

def getVirtualMachineList(esxiIP, esxiUsername, esxiPassword):
    result = callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, r'-l')
    result = result.split('\n')
    i = 0
    for vmx in result:
        if vmx == '':
           result.pop(i)
        i = i + 1
    return result   #返回结果是一个列表

def callVirtualMachineCommadLine(esxiIP, esxiUsername, esxiPassword, cmd):
    if os.path.exists(vSphereCLI):
        output = os.popen(r'"{}" -H {}  -U {} -P {} {} '.format(vSphereCLI,
                                                                esxiIP,
                                                                esxiUsername,
                                                                esxiPassword,
                                                                cmd))
        return output.read()
    else:
        logger.error(r'请检查vSphere CLI是否安装或路径{}是否正确'.format(vSphereCLI))
        sys.exit(1)

def getVmxByVirtualMachineName(ip, username, password, name):
    vmxNamePattern = re.compile(name)
    vmList = getVirtualMachineList(ip, username, password)
    for vmx in vmList:
        if vmxNamePattern.search(vmx):
            return vmx

#vmx = r'/vmfs/volumes/549af783-2bcf0b8c-edd4-001b21c5cdf2/沈晓阳7.0-192.168.5.150/沈晓阳7.0-192.168.5.150.vmx'
#vm_start_soft(r'192.168.4.66',r'root',r'infocore',vmx)
