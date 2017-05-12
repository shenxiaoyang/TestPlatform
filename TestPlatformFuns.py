# -*- coding:utf-8 -*-
import os
import logging
import sys
from xml.dom.minidom import parse
import xml.dom.minidom

#定义日志记录器
logger = logging.getLogger('root.TestPlatformFuns')

#导入全局变量
from TestPlatformGlobalsVar import GROUP_DICT
from TestPlatformGlobalsVar import SERVER_STATE_DICT
from TestPlatformGlobalsVar import IPMI_STATE_DICT

#导入自定义类
from TestPlatformClass import Group
from TestPlatformClass import Server

def read_config_from_xml_file(xml_file):
    if not os.path.exists(xml_file):
        logging.error('配置文件不存在，请检查./Sonfig目录下是否存在相应的配置文件')
        sys.exit(1)
    else:
        logging.debug('读取配置文件 {}'.format(os.path.abspath(xml_file)))
        dom = xml.dom.minidom.parse('./config/ServerConfig.xml')  #打开XML文档
        root = dom.documentElement  #得到xml文档对象的root(config)节点
        groups = root.getElementsByTagName("Group") #得到Group节点列表
        for group in groups:
            new_group = Group()
            if group.hasAttribute("GroupName"):
                new_group.group_name = group.getAttribute("GroupName")
            servers = group.getElementsByTagName("Server")  #得到某个Gourp节点下Server节点列表
            for server in servers:
                new_server = Server()
                if server.hasAttribute("ServerName"):
                    new_server.server_name = server.getAttribute("ServerName")
                if server.hasAttribute("ServerIP"):
                    new_server.server_ip = server.getAttribute("ServerIP")
                    SERVER_STATE_DICT[new_server.server_ip] = ''    #初始化服务器状态字典
                    IPMI_STATE_DICT[new_server.server_ip] = ''
                if server.hasAttribute("ServerUsername"):
                    new_server.username = server.getAttribute("ServerUsername")
                if server.hasAttribute("ServerPassword"):
                    new_server.password = server.getAttribute("ServerPassword")
                if server.hasAttribute("IPMIFlag"):
                    new_server.ipmi_flag = server.getAttribute("IPMIFlag")
                if server.hasAttribute("IPMIIP"):
                    new_server.ipmi_ip = server.getAttribute("IPMIIP")
                if server.hasAttribute("IPMIUsername"):
                    new_server.ipmi_username = server.getAttribute("IPMIUsername")
                if server.hasAttribute("IPMIPassword"):
                    new_server.ipmi_password = server.getAttribute("IPMIPassword")
                if server.hasAttribute("VirtualFlag"):
                    new_server.virtual_flag = server.getAttribute("VirtualFlag")
                if server.hasAttribute("OS"):
                    new_server.os_type = server.getAttribute("OS")
                if server.hasAttribute("VirtualMachineName"):
                    new_server.virtual_machine_name = server.getAttribute("VirtualMachineName")
                if server.hasAttribute("HostIP"):
                    new_server.host_ip = server.getAttribute("HostIP")
                if server.hasAttribute("HostUsername"):
                    new_server.host_username = server.getAttribute("HostUsername")
                if server.hasAttribute("HostPassword"):
                    new_server.host_password = server.getAttribute("HostPassword")
                new_group.addServer(new_server)
            GROUP_DICT[new_group.group_name] = new_group

def save_config_from_xml_file(xml_file):
    doc = xml.dom.minidom.Document()    #在内存中创建一个空文档
    root = doc.createElement('config')  #创建根节点对象
    root.setAttribute('company', 'InfoCore')    #设置根节点属性
    doc.appendChild(root)   #将根节点添加到文档对象中
    for group_name in GROUP_DICT:  #遍历群组配置
        group_node = doc.createElement('Group') #创建Group节点
        group_node.setAttribute('GroupName', group_name)    #设置Group节点属性
        for server_ip in GROUP_DICT[group_name].server_dict:    #遍历服务器配置
            server = GROUP_DICT[group_name].server_dict[server_ip]
            server_node = doc.createElement('Server')   #创建Server节点
            server_node.setAttribute('ServerName',server.server_name)   #设置Server节点的ServerName属性
            server_node.setAttribute('ServerIP',server.server_ip)   #设置Server节点的ServerIP属性
            server_node.setAttribute('ServerUsername', server.username)
            server_node.setAttribute('ServerPassword', server.password)
            server_node.setAttribute('IPMIFlag', server.ipmi_flag)
            server_node.setAttribute('IPMIIP', server.ipmi_ip)
            server_node.setAttribute('IPMIUsername', server.ipmi_username)
            server_node.setAttribute('IPMIPassword', server.ipmi_password)
            server_node.setAttribute('VirtualFlag', server.virtual_flag)
            server_node.setAttribute('OS',server.os_type)
            server_node.setAttribute('VirtualMachineName',server.virtual_machine_name)
            server_node.setAttribute('HostIP',server.host_ip)
            server_node.setAttribute('HostUsername',server.host_username)
            server_node.setAttribute('HostPassword',server.host_password)
            group_node.appendChild(server_node) #把Server节点添加到Group节点中
        root.appendChild(group_node)    #把Group节点添加到根节点中
    fp = open(xml_file,'w')
    doc.writexml(fp, indent='\t', addindent='\t', newl='\n')
    fp.close()

def get_server_struct_by_given_info(given_server_ip=None,given_ipmi_ip=None,given_virtual_machine_name=None):
    if given_server_ip != None:
        for group_name in GROUP_DICT:
            for server_ip in GROUP_DICT[group_name].server_dict:
                server = GROUP_DICT[group_name].server_dict[server_ip]
                if given_server_ip == server_ip:
                    return server

    if given_ipmi_ip != None:
        for group_name in GROUP_DICT:
            for server_ip in GROUP_DICT[group_name].server_dict:
                server = GROUP_DICT[group_name].server_dict[server_ip]
                if server.ipmi_ip == given_ipmi_ip:
                    return server

    if given_virtual_machine_name != None:
        for group_name in GROUP_DICT:
            for server_ip in GROUP_DICT[group_name].server_dict:
                server = GROUP_DICT[group_name].server_dict[server_ip]
                if server.virtual_machine_name == given_virtual_machine_name:
                    return server