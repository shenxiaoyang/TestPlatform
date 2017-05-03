# -*- coding:utf-8 -*-
import datetime
import os
import logging
import time
from subprocess import run
import sys

logger = logging.getLogger('root.InfoCoreTools.WindowsCMD')

global OSNSOLUTION_INSTALL_PATH
global SERVER_TOOL_PATH
OSNSOLUTION_INSTALL_PATH = r'C:\Program Files\Enterprise Information Management\OSNSolution'
SERVER_TOOL_PATH = r'C:\Users\Administrator\Desktop\OSNAutoTest\\'[:-1]

#返回0表示能ping通，返回1表示不能ping通，如果ping不通，则需要4秒超时。
def pingIP(ip):
    #logger.debug(r'ping_ip:尝试ping {}'.format(ip))
    cmd = r"ping {} -n 1 1>nul 2>nul".format(ip)
    #result = os.system(cmd)
    #return result
    result = run(cmd , shell=True)
    return result.returncode

def queryPIDByProcess(ip, username, password, processName):
    cmd = r"tasklist /S {} /U {} /P {}".format(ip,username,password)
    output = os.popen(cmd).read().split('\n')
    for line in output:
        if len(line) != 0:
            line = line.split()
            if line[0] == processName:
                return line[1]

def queryProcess(ip, username, password, processName):
    logger.debug(r'query_process:查询{}的{}服务状态'.format(ip,processName))
    flag = False
    cmd = r"tasklist /S {} /U {} /P {}".format(ip, username, password)
    output = os.popen(cmd).read().split('\n')
    for line in output:
        if len(line) != 0:
            line = line.split()
            if line[0] == processName:
                flag = True
    return flag

def killProcess(ip, username, password, processName):
    tasklistCommandLine = r'tasklist /S {} /U {} /P {} | find "{}"'.format(ip, username, password, processName)
    tasklist = os.popen(tasklistCommandLine).read()
    while tasklist != '':
        logger.debug(r'杀死{}进程[{}]'.format(ip, processName))
        cmd_kill_process = r"taskkill /S {} /U {} /P {} /IM {}".format(ip,username,password,processName)
        output = os.popen(cmd_kill_process)
        logger.debug(output.read().strip())
        time.sleep(1)
        tasklistCommandLine = r'tasklist /S {} /U {} /P {} | find "{}"'.format(ip, username, password, processName)
        tasklist = os.popen(tasklistCommandLine).read()

def killDisktest(ip, username, password):
    logger.debug(r'杀死{}的disktest进程'.format(ip))
    killProcess(ip, username, password, r'DiskTest.exe')

def isDisktestError(ip, username, password, logfile):
    flag = False
    result = ''
    resultFile = logfile.replace(r'C:', r'\\{}\c$'.format(ip))
    local_path = os.path.dirname(__file__)
    os.popen(r"net use \\{} {} /user:{} 2>nul".format(ip, password, username))
    if os.path.exists(resultFile):
        #output = os.popen(r'xcopy {} {}\ /y 2>nul'.format(result_file, local_path))
        #logger.debug(r'读取Disktest.log：{}'.format(output.readline().strip()))
        #local_file = r'{}\DiskTest.log'.format(local_path)
        #time.sleep(1)   #防止程序运行太快，还没拷贝完就检测文件是否存在
        if os.path.getsize(resultFile) != 0:
            flag = True
            fileObject = open(resultFile)
            try:
                result = fileObject.read()
            finally:
                fileObject.close()
        else:
            flag = False
            result = ''
        #os.remove(local_file)
    else:
        flag = True
        result = ''
    return flag,result

def getCurrentDatetimeString():
    logger.debug(r'get_date_time_string:获取当前时间')
    currentTime = datetime.datetime.now()
    currentTimeString = r"%04d%02d%02d%02d%02d%02d" % (currentTime.year,
                                                       currentTime.month,
                                                       currentTime.day,
                                                       currentTime.hour,
                                                       currentTime.minute,
                                                       currentTime.second)
    return currentTimeString

def copyfileTo(ip, username, password, sourceFile, destPath):
    os.popen(r"net use \\{} {} /user:{}".format(ip, password, username))
    os.popen(r"xcopy {} {} /y".format(sourceFile, destPath))
    os.popen(r"net use \\{} /d /y".format(ip))

def collect_server_log(ip, username, password, current_time):
    logging.debug('收集{}日志开始'.format(ip))
    run(r"net use \\{} {} /user:{} 2>nul 1>nul".format(ip, password, username),shell=True)
    localLogPath = r'{}\log\{}\{}'.format(os.path.dirname(os.path.abspath(sys.argv[0])),
                                          current_time,
                                          str(ip).replace(r'.', r'_'))
    remoteOSNSolutionLog = OSNSOLUTION_INSTALL_PATH.replace(r'C:', r'\\{}\c$'.format(ip))
    run(r'xcopy "{}\Repository\*"  "{}\OSN_log\" /y 2>nul 1>nul'.format(remoteOSNSolutionLog, localLogPath),shell=True)
    run(r'xcopy "{}\*.log" "{}\OSN_log\" /y 2>nul 1>nul'.format(remoteOSNSolutionLog, localLogPath),shell=True)
    run(r'xcopy "{}\*.cfg" "{}\OSN_log\" /y 2>nul 1>nul'.format(remoteOSNSolutionLog, localLogPath),shell=True)
    run(r'xcopy "{}\*.txt" "{}\OSN_log\" /y 2>nul 1>nul'.format(remoteOSNSolutionLog, localLogPath),shell=True)
    run(r'xcopy "{}\*.etl" "{}\OSN_log\" /y 2>nul 1>nul'.format(remoteOSNSolutionLog, localLogPath),shell=True)
    remoteWindowsDump = r"\\{}\c$\Windows".format(ip)
    run(r'xcopy "{}\*.dmp" "{}\dump\" /y 2>nul 1>nul'.format(remoteWindowsDump, localLogPath),shell=True)
    remoteDebugLog = r'{}*.log'.format(SERVER_TOOL_PATH).replace(r'C:', r'\\{}\c$'.format(ip))
    run(r'xcopy "{}" "{}\debugview\" /y 2>nul 1>nul'.format(remoteDebugLog, localLogPath),shell=True)
    run(r"net use \\{} /d /y 1>nul".format(ip),shell=True)
    logging.debug('收集{}日志完毕,日志存放路径为{}'.format(ip,localLogPath))