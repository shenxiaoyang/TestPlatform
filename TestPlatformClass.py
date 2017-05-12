# -*- coding:utf-8 -*-
import collections
import logging

#定义日志记录器
logger = logging.getLogger('root.TestPlatformClass')

class Group:
    def __init__(self):
        self.group_name = ''
        self.group_id = ''
        self.group_role = ''
        self.server_dict = collections.OrderedDict()
    def addServer(self, new_server):
        self.server_dict[new_server.server_ip] = new_server

class Server:
    def __init__(self):
        self.server_name = ''
        self.server_id = ''
        self.server_ip = ''
        self.server_state = ''
        self.username = ''
        self.password = ''
        self.ipmi_flag = '' #0未配置，1已配置，其他未知
        self.ipmi_ip = ''
        self.ipmi_username = ''
        self.ipmi_password = ''
        self.virtual_flag = ''
        self.os_type = ''
        self.virtual_machine_name = ''
        self.host_ip = ''
        self.host_username = ''
        self.host_password = ''
