# -*- coding:utf-8 -*-
import threading
import logging
import time

#定义日志记录器
logger = logging.getLogger('root.TestPlatformThread')

#导入自定义模块
from InfoCoreTools import WindowsCMD,vSphereCLI,IPMI

#导入全局变量
from TestPlatformGlobalsVar import GROUP_DICT
from TestPlatformGlobalsVar import EVENT
from TestPlatformGlobalsVar import SERVER_STATE_DICT
from TestPlatformGlobalsVar import IPMI_STATE_DICT

#后台数据刷新线程
#1、每隔5秒刷新一次服务器状态，
class RefreshStateThread(threading.Thread):
    daemon = True   #设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, name, parent=None):
        super(RefreshStateThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
    def run(self):
        while 1:
            logging.debug('{} 定时刷新状态'.format(self.thread_name))
            for group_name in GROUP_DICT:   #遍历所有群组
                for server_ip in GROUP_DICT[group_name].server_dict:    #遍历群组下所有的服务器
                    server = GROUP_DICT[group_name].server_dict[server_ip]
                    get_ping_state_thread = GetPingStateThread(ip=server_ip)
                    get_ping_state_thread.start()   #开一个ping线程，用于获取服务器状态
                    if server.ipmi_flag == '1': #判断是否配置了IPMI
                        get_power_state_thread = GetPowerStateFromIPMIThread(server.server_ip,
                                                                             server.ipmi_ip,
                                                                             server.ipmi_username,
                                                                             server.ipmi_password)
                        get_power_state_thread.start()  #开一个获取IPMI电源状态的线程
            time.sleep(5)   #每隔5秒后台刷新一次状态

class GetPingStateThread(threading.Thread):
    daemon = True
    def __init__(self, ip, name=None, parent=None):
        super(GetPingStateThread, self).__init__(parent)
        self.thread_name = name
        self.ip = ip
    def run(self):
        #logging.debug('GetPingStateThread:ping {}'.format(self.ip))
        old_state = SERVER_STATE_DICT[self.ip]
        new_state = WindowsCMD.pingIP(self.ip)
        if new_state != old_state:
            SERVER_STATE_DICT[self.ip] = new_state
            EVENT.set()

class GetPowerStateFromIPMIThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, server_ip, ipmi_ip, ipmi_username, ipmi_password, name=None, parent=None):
        super(GetPowerStateFromIPMIThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.server_ip = server_ip
        self.ipmi_ip = ipmi_ip
        self.ipmi_username = ipmi_username
        self.ipmi_password = ipmi_password

    def run(self):
        logging.debug('GetPowerStateFromIPMIThread：获取{}电源状态'.format(self.ipmi_ip))
        old_power_state = IPMI_STATE_DICT[self.server_ip]
        new_power_state = IPMI.powerStatus(self.ipmi_ip, self.ipmi_username, self.ipmi_password)
        if new_power_state != old_power_state:
            IPMI_STATE_DICT[self.server_ip] = new_power_state
            EVENT.set()

class CollectServerLogsThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, server_ip, username, password, time, name=None, parent=None):
        super(CollectServerLogsThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.server_ip = server_ip
        self.username = username
        self.password = password
        self.time = time

    def run(self):
        logging.debug('准备收集{}日志'.format(self.server_ip))
        WindowsCMD.collect_server_log(self.server_ip, self.username, self.password, self.time)

class StartVirtualMachineThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, host_ip,host_username, host_password, virtual_machine_name, name=None, parent=None):
        super(StartVirtualMachineThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.host_ip = host_ip
        self.host_username = host_username
        self.host_password = host_password
        self.virtual_machine_name = virtual_machine_name

    def run(self):
        logging.debug('StartVirtualMachineThread：{}打开VM电源'.format(self.virtual_machine_name))
        vSphereCLI.startVirtualMachineHard(self.host_ip,
                                           self.host_username,
                                           self.host_password,
                                           self.virtual_machine_name)

class StopVirtualMachineThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, host_ip,host_username, host_password, virtual_machine_name, name=None, parent=None):
        super(StopVirtualMachineThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.host_ip = host_ip
        self.host_username = host_username
        self.host_password = host_password
        self.virtual_machine_name = virtual_machine_name

    def run(self):
        logging.debug('StartVirtualMachineThread：{}关闭VM电源'.format(self.virtual_machine_name))
        vSphereCLI.stopVirtualMachineHard(self.host_ip,
                                          self.host_username,
                                          self.host_password,
                                          self.virtual_machine_name)

class PowerOnFromIPMIThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, ipmi_ip,ipmi_username, ipmi_password, name=None, parent=None):
        super(PowerOnFromIPMIThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.ipmi_ip = ipmi_ip
        self.ipmi_username = ipmi_username
        self.ipmi_password = ipmi_password

    def run(self):
        logging.debug('PowerOnFromIPMIThread：{}打开电源'.format(self.ipmi_ip))
        IPMI.powerOn(self.ipmi_ip,self.ipmi_username,self.ipmi_password)

class PowerOffFromIPMIThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, ipmi_ip,ipmi_username, ipmi_password, name=None, parent=None):
        super(PowerOffFromIPMIThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.ipmi_ip = ipmi_ip
        self.ipmi_username = ipmi_username
        self.ipmi_password = ipmi_password

    def run(self):
        logging.debug('PowerOnFromIPMIThread：{}关闭电源'.format(self.ipmi_ip))
        IPMI.powerOff(self.ipmi_ip,self.ipmi_username,self.ipmi_password)

class CopyTestToolsToThread(threading.Thread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    def __init__(self, server_ip, username, password, name=None, parent=None):
        super(CopyTestToolsToThread, self).__init__(parent)
        self.thread_name = name  # 将传递过来的name构造到类中的name
        self.server_ip = server_ip
        self.username = username
        self.password = password

    def run(self):
        logging.debug('CopyTestToolsToThread：{}关闭电源'.format(self.server_ip))
        WindowsCMD.copyTestToolTo(self.server_ip,self.username,self.password)