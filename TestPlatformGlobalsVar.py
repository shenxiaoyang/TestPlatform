# -*- coding:utf-8 -*-
import collections
import threading

global GROUP_DICT
global EVENT
global SERVER_STATE_DICT
global IPMI_STATE_DICT
global SERVICE_LIST
global SERVICE_STATE_DICT
GROUP_DICT = collections.OrderedDict()
EVENT = threading.Event()
SERVER_STATE_DICT = {}  #0在线 1离线
IPMI_STATE_DICT = {}
SERVICE_STATE_DICT = {}
SERVICE_LIST = ['OSNMirHBService',
                'OSNScheduleService',
                'OSNSPlatformService',
                'OSNSDetectService',
                'OSNService',
                'OSNHBService']