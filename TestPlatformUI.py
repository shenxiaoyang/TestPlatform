# -*- coding: utf-8 -*-
#导入系统模块
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import time
import logging

#定义日志记录器
logger = logging.getLogger('root.TestPlatformUI')

#导入自定义模块
from InfoCoreTools import WindowsCMD,PsExc64

#导入全局变量
from TestPlatformGlobalsVar import GROUP_DICT
from TestPlatformGlobalsVar import EVENT
from TestPlatformGlobalsVar import SERVER_STATE_DICT
from TestPlatformGlobalsVar import IPMI_STATE_DICT
from TestPlatformGlobalsVar import SERVICE_LIST


#导入线程类
from TestPlatformThread import RefreshStateThread
from TestPlatformThread import CopyTestToolsToThread
from TestPlatformThread import CollectServerLogsThread
from TestPlatformThread import StartVirtualMachineThread
from TestPlatformThread import StopVirtualMachineThread
from TestPlatformThread import PowerOnFromIPMIThread
from TestPlatformThread import PowerOffFromIPMIThread

#导入类模块
from TestPlatformClass import Group
from TestPlatformClass import Server

#导入自定义函数
from TestPlatformFuns import save_config_from_xml_file

class MonitorUIThread(QThread):
    daemon = True  # 设置True表示主线程关闭的时候，这个线程也会被关闭。[一般来说主线是用户UI线程]
    signal_update_tree_server_state = pyqtSignal()  # 自定义信号
    signal_update_tab_1 = pyqtSignal()

    def __init__(self, event ,parent=None):
        super(MonitorUIThread, self).__init__(parent)
        self.event = event

    def run(self):
        while 1:
            self.event.wait()   #阻塞线程，等待外部事件响应
            self.signal_update_tree_server_state.emit() #发射信号
            self.signal_update_tab_1.emit()
            self.event.clear()  #重新设置线程阻塞

class MainWindows(QMainWindow):   #重载主窗体类，继承QtWidgets.QMainWindow
    def __init__(self, parent=None):    #主窗体构造函数
        # super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(MainWindows,self).__init__(parent)
        self.init_ui()  #初始化主窗口UI
        self.connect_all_signal_slot()  # 初始化信号槽
        self.start_refresh_state_thread()   #启动界面数据刷新线程
        self.start_monitor_ui_thread()  #启动后台数据定时刷新线程

    # 设置UI函数，MainWindows类的布局均由它完成
    def init_ui(self):
        logging.debug('初始化加载UI布局')
        self.setObjectName("MainWindow")  # 设置窗体对象名
        self.resize(830, 370)  # 设置窗体的大小
        self.setFixedSize(self.width(), self.height())  # 固定窗口大小
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)    #设置窗口置顶

        # 设置treeWidget
        self.treeWidget = QTreeWidget(self)  # 在栅格中创建一个treeWidget
        self.treeWidget.setGeometry(QRect(10, 60, 500, 300))  # 设置栅格布局控件大小
        self.treeWidget.setObjectName("treeWidget")  # 设置树控件的对象名
        self.treeWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 设置垂直滚动条策略：关
        self.treeWidget.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContentsOnFirstShow)
        self.treeWidget.setItemsExpandable(False)  # 设置节点不可手动展开关闭
        self.treeWidget.setObjectName("treeWidget")  # 设置treeWidget的Object名
        self.treeWidget.setColumnCount(6)  # 设置6列
        self.treeWidget.setAllColumnsShowFocus(True)
        self.treeWidget.header().setVisible(False)  # 隐藏treeWidget头
        self.treeWidget.setColumnWidth(0, 170)  # 设置第一列列宽
        self.treeWidget.setColumnWidth(1, 60)
        self.treeWidget.setColumnWidth(2, 60)
        self.treeWidget.setColumnWidth(3, 60)
        self.treeWidget.setColumnWidth(4, 60)
        self.treeWidget.setColumnWidth(5, 60)
        self.load_tree()  # 加载树列表的数据

        # 设置tabWidget
        self.tabWidget = QTabWidget(self)  # 在栅格中创建一个tabWidget
        self.tabWidget.setGeometry(QRect(520, 60, 300, 300))  # 设置栅格布局控件大小
        self.tabWidget.setObjectName("tabWidget")  # 设置tabWidget的Object名
        self.tab_1 = QWidget()
        self.tab_1.setObjectName("tab_1")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tabWidget.setCurrentIndex(0)  # 设置tab默认的选中页

        # 设置tabWidgt中内容
        self.gridLayoutWidget_2 = QWidget(self.tab_1)
        self.gridLayoutWidget_2.setGeometry(QRect(10, 10, 450, 270))
        self.gridLayoutWidget_2.setObjectName('gridLayoutWidget_2')
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName('gridLayout_2')
        self.label_username = QLabel(self.gridLayoutWidget_2)
        self.label_username.setObjectName("label_group_name")
        self.gridLayout_2.addWidget(self.label_username, 3, 1, 1, 1)
        self.label_server_state = QLabel(self.gridLayoutWidget_2)
        self.label_server_state.setObjectName("label_server_state")
        self.gridLayout_2.addWidget(self.label_server_state, 4, 1, 1, 1)
        self.label_ipmi_state = QLabel(self.gridLayoutWidget_2)
        self.label_ipmi_state.setObjectName("label_ipmi_state")
        self.gridLayout_2.addWidget(self.label_ipmi_state, 5, 1, 1, 1)
        self.label_group_name = QLabel(self.gridLayoutWidget_2)
        self.label_group_name.setObjectName("label_group_name")
        self.gridLayout_2.addWidget(self.label_group_name, 0, 1, 1, 1)
        self.label_server_name = QLabel(self.gridLayoutWidget_2)
        self.label_server_name.setObjectName("label_server_name")
        self.gridLayout_2.addWidget(self.label_server_name, 1, 1, 1, 1)
        self.label_server_ip = QLabel(self.gridLayoutWidget_2)
        self.label_server_ip.setObjectName("label_server_ip")
        self.gridLayout_2.addWidget(self.label_server_ip, 2, 1, 1, 1)
        self.label_ipmi_config = QLabel(self.gridLayoutWidget_2)
        self.label_ipmi_config.setObjectName("label_ipmi_config")
        self.gridLayout_2.addWidget(self.label_ipmi_config, 6, 1, 1, 1)

        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        # 设置树的右键菜单
        self.rightMenu = QMenu(self.treeWidget)  # 在树中创建右键菜单
        self.action_collect_logs = QAction(self.rightMenu)  # 创建菜单项[收集日志]
        self.action_normal_shutdown = QAction(self.rightMenu)  # 创建菜单项[正常关机]
        self.action_ipmi_poweroff = QAction(self.rightMenu)  # 创建菜单项[IPMI关机]
        self.action_ipmi_poweron = QAction(self.rightMenu)  # 创建菜单项[IPMI开机]
        self.action_bang = QAction(self.rightMenu)  # 创建菜单项[bang]
        self.action_modify_server_config = QAction(self.rightMenu)  # 创建菜单项[修改配置]
        self.action_start_service = QAction(self.rightMenu)  # 创建菜单项[启动服务]
        self.action_stop_service = QAction(self.rightMenu)  # 创建菜单项[停止服务]
        self.action_set_service_start_on = QAction(self.rightMenu)  # 创建菜单项[开启服务自启]
        self.action_set_service_start_off = QAction(self.rightMenu)  # 创建菜单项[关闭服务自启]
        self.action_virtual_machine_power_on = QAction(self.rightMenu) #创建菜单项[VM打开电源]
        self.action_virtual_machine_power_off = QAction(self.rightMenu) #创建菜单项[VM关闭电源]

        # 把菜单项添加到右键中
        self.rightMenu.addAction(self.action_collect_logs)
        self.rightMenu.addSeparator()  # 添加分割符
        self.rightMenu.addAction(self.action_normal_shutdown)
        self.rightMenu.addAction(self.action_ipmi_poweroff)
        self.rightMenu.addAction(self.action_ipmi_poweron)
        self.rightMenu.addAction(self.action_bang)
        self.rightMenu.addSeparator()  # 添加分割符
        self.rightMenu.addAction(self.action_modify_server_config)
        self.rightMenu.addSeparator()  # 添加分割符
        self.rightMenu.addAction(self.action_start_service)
        self.rightMenu.addAction(self.action_stop_service)
        self.rightMenu.addAction(self.action_set_service_start_on)
        self.rightMenu.addAction(self.action_set_service_start_off)
        self.rightMenu.addSeparator()  # 添加分割符
        self.rightMenu.addAction(self.action_virtual_machine_power_on)
        self.rightMenu.addAction(self.action_virtual_machine_power_off)

        # 设置水平布局控件
        self.horizontalLayoutWidget = QWidget(self)  # 在mainWindows窗体中创建一个水平布局控件
        self.horizontalLayoutWidget.setGeometry(QRect(10, 25, 360, 30))  # 设置水平布局控件大小
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")  # 设置水平布局控件的Object名
        self.horizontalLayout = QHBoxLayout(self.horizontalLayoutWidget)  # 创建水平布局控件
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)  # 设置水平布局边距
        self.horizontalLayout.setObjectName("horizontalLayout")  # 设置水平布局Object名

        # 设置按钮
        self.btn_addServer = QPushButton(self.horizontalLayoutWidget)  # 在水平布局中添加按钮[添加服务器]
        self.btn_addServer.setObjectName("bt_addServer")  # 设置按钮Object名
        self.horizontalLayout.addWidget(self.btn_addServer)  # 把按钮放到水平布局中

        self.btn_delServer = QPushButton(self.horizontalLayoutWidget)  # 在水平布局中添加按钮[删除]
        self.btn_delServer.setObjectName("bt_delServer")
        self.btn_delServer.setDisabled(True)
        self.horizontalLayout.addWidget(self.btn_delServer)  # 把按钮放到水平布局中

        self.btn_collect_log = QPushButton(self.horizontalLayoutWidget)  # 在水平布局中添加按钮[刷新]
        self.btn_collect_log.setObjectName("btn_refresh")
        self.horizontalLayout.addWidget(self.btn_collect_log)  # 把按钮放到水平布局中

        self.btn_copy_tools = QPushButton(self.horizontalLayoutWidget)  # 在水平布局中添加按钮[复制工具]
        self.btn_copy_tools.setObjectName("btn_copy_tools")
        self.horizontalLayout.addWidget(self.btn_copy_tools)  # 把按钮放到水平布局中

        self.btn_sync_system_time = QPushButton(self.horizontalLayoutWidget)  # 在水平布局中添加按钮[校准时间]
        self.btn_sync_system_time.setObjectName("btn_sync_system_time")
        self.horizontalLayout.addWidget(self.btn_sync_system_time)  # 把按钮放到水平布局中

        # 菜单栏
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(QRect(0, 10, 700, 25))
        self.menuBar.setObjectName("menuBar")
        self.menu_config = QMenu(self.menuBar)
        self.menu_config.setObjectName("menu_config")
        self.setMenuBar(self.menuBar)
        self.actionOpenSystemConfig = QAction(self)
        self.actionOpenSystemConfig.setObjectName("actionOpenSystemConfig")
        self.menu_config.addAction(self.actionOpenSystemConfig)
        self.menuBar.addAction(self.menu_config.menuAction())

        self.retranslateUi()  # 加载retranslateUi函数
        QMetaObject.connectSlotsByName(self)  # 关联自动连接信号槽

    #MainWindows类的本地化函数
    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "InfoCore TestPlatform"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "摘要"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "详细信息"))
        self.btn_delServer.setText(_translate("MainWindow", "删除"))
        self.btn_addServer.setText(_translate("MainWindow", "添加服务器"))
        self.btn_collect_log.setText(_translate("MainWindow", "收集日志"))
        self.btn_copy_tools.setText(_translate("MainWindow", "复制工具"))
        self.btn_sync_system_time.setText(_translate("MainWindow", "校准时间"))
        self.menu_config.setTitle(_translate("MainWindow", "配置"))
        self.actionOpenSystemConfig.setText(_translate("MainWindow", "系统设置"))

        self.action_normal_shutdown.setText('正常关机')
        self.action_ipmi_poweroff.setText('IPMI关机')
        self.action_ipmi_poweron.setText('IPMI开机')
        self.action_bang.setText('Bang')
        self.action_collect_logs.setText('收集日志')
        self.action_modify_server_config.setText('修改配置')
        self.action_start_service.setText('启动服务')
        self.action_stop_service.setText('停止服务')
        self.action_set_service_start_on.setText('开启服务自启')
        self.action_set_service_start_off.setText('关闭服务自启')
        self.action_virtual_machine_power_on.setText('VM打开电源')
        self.action_virtual_machine_power_off.setText('VM关闭电源')

    # 设置信号槽
    def connect_all_signal_slot(self):
        logging.debug('加载信号槽设置')
        self.btn_addServer.clicked.connect(self.clicked_add_server_btn)  # 点击按钮[添加服务器]弹出对话框
        self.btn_delServer.clicked.connect(self.clicked_del_server_btn)  # 点击按钮[删除]
        self.treeWidget.itemSelectionChanged.connect(self.tree_item_selection_changed)  # 树的项选中变更事件
        self.treeWidget.customContextMenuRequested.connect(self.showRightMenu)  # 树的右键菜单
        self.action_normal_shutdown.triggered.connect(self.triggered_action_normal_shutdown)
        self.action_bang.triggered.connect(self.triggered_action_bang)
        self.action_collect_logs.triggered.connect(
            lambda: self.triggered_action_collect_logs(WindowsCMD.getCurrentDatetimeString()))
        self.btn_collect_log.clicked.connect(self.start_collect_all_logs_thread)
        self.action_modify_server_config.triggered.connect(self.triggered_action_modify_server_config)
        self.action_start_service.triggered.connect(self.triggered_action_start_service)
        self.action_stop_service.triggered.connect(self.triggered_action_stop_service)
        self.action_set_service_start_on.triggered.connect(self.triggered_action_set_service_start_on)
        self.action_set_service_start_off.triggered.connect(self.triggered_action_set_service_start_off)
        self.action_virtual_machine_power_on.triggered.connect(self.triggered_action_virtual_machine_power_on)
        self.action_virtual_machine_power_off.triggered.connect(self.triggered_action_virtual_machine_power_off)
        self.action_ipmi_poweron.triggered.connect(self.triggered_action_ipmi_power_on)
        self.action_ipmi_poweroff.triggered.connect(self.triggered_action_ipmi_power_off)
        self.btn_copy_tools.clicked.connect(self.clicked_copy_tools_btn)

    def start_monitor_ui_thread(self):
        logging.debug('启动界面数据刷新线程')
        self.monitor_ui_thread = MonitorUIThread(EVENT)    #注册事件器
        self.monitor_ui_thread.start()  #启动线程
        self.monitor_ui_thread.signal_update_tree_server_state.connect(self.update_tree_state)   #设置信号槽[用于更新树列表]
        self.monitor_ui_thread.signal_update_tab_1.connect(self.tree_item_selection_changed)

    def start_refresh_state_thread(self):
        logging.debug('启动后台数据定时刷新线程')
        self.refresh_state_thread = RefreshStateThread('RefreshStateThread')
        self.refresh_state_thread.start()

    def start_collect_all_logs_thread(self):
        current_time = WindowsCMD.getCurrentDatetimeString()
        for group_name in GROUP_DICT:
            for server_ip in GROUP_DICT[group_name].server_dict:
                server = GROUP_DICT[group_name].server_dict[server_ip]
                if SERVER_STATE_DICT[server_ip] == 0:
                    collect_server_log_thread = CollectServerLogsThread(server.server_ip,
                                                                        server.username,
                                                                        server.password,
                                                                        current_time)
                    collect_server_log_thread.start()

    # 显示右键菜单
    def showRightMenu(self):
        self.rightMenu.exec_(QCursor.pos())

    def triggered_action_ipmi_power_on(self):
        logging.debug('右键[IPMI开机]')
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            server = GROUP_DICT[group_name].server_dict[server_ip]
                            ipmi_power_on_thread= PowerOnFromIPMIThread(server.ipmi_ip,
                                                                        server.ipmi_username,
                                                                        server.ipmi_password)
                            ipmi_power_on_thread.start()

    def triggered_action_ipmi_power_off(self):
        logging.debug('右键[IPMI关机]')
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            server = GROUP_DICT[group_name].server_dict[server_ip]
                            ipmi_power_off_thread= PowerOffFromIPMIThread(server.ipmi_ip,
                                                                          server.ipmi_username,
                                                                          server.ipmi_password)
                            ipmi_power_off_thread.start()

    def triggered_action_virtual_machine_power_on(self):
        logging.debug('右键[VM打开电源]')
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            server = GROUP_DICT[group_name].server_dict[server_ip]
                            start_vm_thread = StartVirtualMachineThread(server.host_ip,
                                                                        server.host_username,
                                                                        server.host_password,
                                                                        server.virtual_machine_name)
                            start_vm_thread.start()


    def triggered_action_virtual_machine_power_off(self):
        logging.debug('右键[VM关闭电源]')
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            server = GROUP_DICT[group_name].server_dict[server_ip]
                            stop_vm_thread = StopVirtualMachineThread(server.host_ip,
                                                                      server.host_username,
                                                                      server.host_password,
                                                                      server.virtual_machine_name)
                            stop_vm_thread.start()

    def triggered_action_start_service(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  #判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            select_username = GROUP_DICT[group_name].server_dict[server_ip].username
                            select_password = GROUP_DICT[group_name].server_dict[server_ip].password
                for service_name in SERVICE_LIST:
                    PsExc64.startRemoteMachineService(select_server_ip,select_username,select_password,service_name)

    def triggered_action_stop_service(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            select_username = GROUP_DICT[group_name].server_dict[server_ip].username
                            select_password = GROUP_DICT[group_name].server_dict[server_ip].password
                for service_name in SERVICE_LIST:
                    PsExc64.stopRemoteMachineService(select_server_ip, select_username, select_password,service_name)
                    time.sleep(1)   #服务关闭后延迟1秒，防止有依赖的服务关闭失败

    def triggered_action_set_service_start_on(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  #判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            select_username = GROUP_DICT[group_name].server_dict[server_ip].username
                            select_password = GROUP_DICT[group_name].server_dict[server_ip].password
                for service_name in SERVICE_LIST:
                    PsExc64.chkconfigRemoteMachineServiceOn(select_server_ip,
                                                            select_username,
                                                            select_password,
                                                            service_name)

    def triggered_action_set_service_start_off(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            select_username = GROUP_DICT[group_name].server_dict[server_ip].username
                            select_password = GROUP_DICT[group_name].server_dict[server_ip].password
                for service_name in SERVICE_LIST:
                    PsExc64.chkconfigRemoteMachineServiceOff(select_server_ip,
                                                             select_username,
                                                             select_password,
                                                             service_name)


    #右键[收集日志]按钮事件处理
    def triggered_action_collect_logs(self, time=None):
        logging.debug('右键[收集日志]')
        if time:
            current_time = time
        else:
            current_time = WindowsCMD.getCurrentDatetimeString()

        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  #判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        server = GROUP_DICT[group_name].server_dict[server_ip]
                        if select_server_ip == server_ip:
                            collect_server_log_thread = CollectServerLogsThread(server.server_ip,
                                                                                server.username,
                                                                                server.password,
                                                                                current_time)
                            collect_server_log_thread.start()

    #右键[修改配置]事件处理
    def triggered_action_modify_server_config(self):
        selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
        if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
            pass
        elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
            pass
        else:  # 判断是否选中Server节点
            select_server_ip = selected_item.text(0)
        modify_server_config_dlg = ModifyServerConfigDlg(self, selected_node_ip=select_server_ip)
        modify_server_config_dlg.sin1.connect(self.update_tree)
        modify_server_config_dlg.show()

    # 右键[正常关机]事件处理
    def triggered_action_normal_shutdown(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            select_username = GROUP_DICT[group_name].server_dict[server_ip].username
                            select_password = GROUP_DICT[group_name].server_dict[server_ip].password
                PsExc64.shutdownRemoteMachine(select_server_ip, select_username, select_password)

    # 右键[bang]事件处理
    def triggered_action_bang(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  # 获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  # 判断是否选中根节点
                pass
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 判断是否选中Group节点
                pass
            else:  # 判断是否选中Server节点
                select_server_ip = selected_item.text(0)
                for group_name in GROUP_DICT:
                    for server_ip in GROUP_DICT[group_name].server_dict:
                        if select_server_ip == server_ip:
                            select_username = GROUP_DICT[group_name].server_dict[server_ip].username
                            select_password = GROUP_DICT[group_name].server_dict[server_ip].password
                            PsExc64.bangRemoteMachine(select_server_ip, select_username, select_password)

    #树项选中事件处理
    def tree_item_selection_changed(self):
        if self.treeWidget.selectedItems() != []:
            selected_item = self.treeWidget.selectedItems()[0]  #获取选中节点
            if selected_item == self.treeWidget.topLevelItem(0):  #判断是否选中根节点
                logging.debug('选中了根节点')
                self.btn_delServer.setDisabled(True)    #把删除服务器按钮标记失效
                self.rightMenu.setDisabled(True)
            elif selected_item.parent() == self.treeWidget.topLevelItem(0):  # 选中Group节点
                logging.debug('选中了Group节点：{}'.format(selected_item.text(0)))
                self.btn_delServer.setDisabled(False)   #把删除服务器按钮标记可用
                self.rightMenu.setDisabled(True)
            else:  # 选中Server节点
                logging.debug('选中了Server节点：{}'.format(selected_item.text(0)))
                self.btn_delServer.setDisabled(False)   #把删除服务器按钮标记可用
                server_node = GROUP_DICT[selected_item.parent().text(0)].server_dict[selected_item.text(0)]
                self.label_username.setText("当前设置用户：{}".format(server_node.username))   #设置tab[摘要]信息
                self.label_group_name.setText("所属群组：{}".format(selected_item.parent().text(0)))
                self.label_server_name.setText("服务器名：{}".format(server_node.server_name))
                self.label_server_ip.setText("服务器IP地址：{}".format(server_node.server_ip))
                if SERVER_STATE_DICT[server_node.server_ip] == '':  # 设置状态
                    self.label_server_state.setText("服务器状态：未知")
                    self.rightMenu.setDisabled(True)
                elif SERVER_STATE_DICT[server_node.server_ip] == 1:
                    self.label_server_state.setText("服务器状态：离线")
                    self.rightMenu.setDisabled(False)
                    self.action_bang.setDisabled(True)
                    self.action_collect_logs.setDisabled(True)
                    self.action_normal_shutdown.setDisabled(True)
                else:
                    self.rightMenu.setDisabled(False)
                    self.label_server_state.setText("服务器状态：在线")
                    self.action_bang.setDisabled(False)
                    self.action_collect_logs.setDisabled(False)
                    self.action_normal_shutdown.setDisabled(False)

    # 打开添加服务器对话框
    def clicked_add_server_btn(self):
        add_server_dlg = AddServerDlg(self)  # 创建对话框
        add_server_dlg.sin1.connect(self.update_tree)  # 设置自定义信号槽连接（用于更新树列表）
        add_server_dlg.show()  # 显示对话框

    #删除按钮事件处理
    def clicked_del_server_btn(self):
        selected_item = self.treeWidget.selectedItems()[0]
        if selected_item.parent().parent() != None: #判断选中节点是否是server节点
            del_group_name = selected_item.parent().text(0)
            del_server_ip = selected_item.text(0)
            GROUP_DICT[del_group_name].server_dict.pop(del_server_ip)
            SERVER_STATE_DICT.pop(del_server_ip)
            IPMI_STATE_DICT.pop(del_server_ip)
        else:
            del_group_name = selected_item.text(0)
            for server_ip in GROUP_DICT[del_group_name].server_dict:
                SERVER_STATE_DICT.pop(server_ip)
                IPMI_STATE_DICT.pop(server_ip)
            GROUP_DICT.pop(del_group_name)
        save_config_from_xml_file('.\config\ServerConfig.xml')
        self.update_tree()
        self.btn_delServer.setDisabled(True)    #删除后失去当前选中焦点,设置删除按钮不可用


    def clicked_copy_tools_btn(self):
        for group_name in GROUP_DICT:
            for server_ip in GROUP_DICT[group_name].server_dict:
                if SERVER_STATE_DICT[server_ip] == 0:
                    server = GROUP_DICT[group_name].server_dict[server_ip]
                    copy_test_tools_thread = CopyTestToolsToThread(server.server_ip,server.username,server.password)
                    copy_test_tools_thread.start()

    def load_tree(self):
        logging.debug('加载整个树形列表')
        root_item = QTreeWidgetItem(self.treeWidget)  # 创建tree的根节点
        root_item.setText(0, 'InfoCore测试平台')  # 设置根节点文本
        root_item.setText(1, '状态')
        root_item.setText(2, '服务状态')
        root_item.setText(3, 'IPMI状态')
        root_item.setText(4, '实/虚机')
        root_item.setText(5, '操作系统')
        self.treeWidget.expandItem(root_item)  # 展开根节点
        for group_name in GROUP_DICT:
            group_item = QTreeWidgetItem(root_item)  # 创建Group节点
            group_item.setText(0, group_name)  # 设置节点显示文本
            self.treeWidget.expandItem(group_item)  # 展开Group节点
            for server_ip in GROUP_DICT[group_name].server_dict:
                server_item = QTreeWidgetItem(group_item)  # 创建Server子节点
                server_item.setText(0, server_ip)   #设置IP地址
                server = GROUP_DICT[group_name].server_dict[server_ip]
                if server.virtual_flag == '1':   #设置实/虚机
                    server_item.setText(4, '实体机')
                else:
                    server_item.setText(4, '虚拟机')

                if server.os_type == 'Linux':
                    server_item.setText(5, 'Linux')
                elif server.os_type == 'Windows':
                    server_item.setText(5, 'Windows')
                else:
                    server_item.setText(5, '未知')
        self.update_tree_state()

    def update_tree_state(self):
        root_item = self.treeWidget.topLevelItem(0)
        for i in range(0,root_item.childCount()):
            group_item = root_item.child(i)
            for j in range(0,group_item.childCount()):
                server_item = group_item.child(j)
                #更新树的服务器状态
                if SERVER_STATE_DICT[server_item.text(0)] == '':
                    server_item.setText(1, '未获取到')
                elif SERVER_STATE_DICT[server_item.text(0)] == 1:
                    server_item.setText(1, '离线')
                else:
                    server_item.setText(1, '在线')

                if IPMI_STATE_DICT[server_item.text(0)] == 1:
                    server_item.setText(3, '电源打开')
                elif IPMI_STATE_DICT[server_item.text(0)] == 0:
                    server_item.setText(3, '电源关闭')
                else:
                    server_item.setText(3, '未知')

    #更新整个树
    def update_tree(self):
        if self.treeWidget.topLevelItem(0) != None: #判断根节点是否存在
            self.treeWidget.itemSelectionChanged.disconnect(self.tree_item_selection_changed)   #断开信号槽
            self.treeWidget.clear() #清理整个树
        self.load_tree()    #重新载入整个树
        self.treeWidget.itemSelectionChanged.connect(self.tree_item_selection_changed)  #重新设置信号槽

class SystemConfigDlg(QDialog):
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(SystemConfigDlg,self).__init__(parent)
        self.setup_ui()

class AddServerDlg(QDialog):
    sin1 = pyqtSignal() #自定义信号
    def __init__(self, parent=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(AddServerDlg,self).__init__(parent)
        self.setObjectName("AddServerDialog")
        self.init_ui()

    def init_ui(self):
        self.resize(450, 300)
        self.setFixedSize(self.width(), self.height())
        self.setSizeGripEnabled(True)

        #添加栅格布局1
        self.gridLayoutWidget_1 = QWidget(self)
        self.gridLayoutWidget_1.setGeometry(QRect(10, 10, 430, 100))
        self.gridLayoutWidget_1.setObjectName("gridLayoutWidget_1")
        self.gridLayout = QGridLayout(self.gridLayoutWidget_1)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")

        #设置界面上的各个标签布局
        self.label_group_name = QLabel(self.gridLayoutWidget_1)
        self.label_group_name.setObjectName("label_group_name")
        self.gridLayout.addWidget(self.label_group_name, 1, 1, 1, 1)

        self.label_server_ip = QLabel(self.gridLayoutWidget_1)
        self.label_server_ip.setObjectName("label_server_ip")
        self.gridLayout.addWidget(self.label_server_ip, 2, 1, 1, 1)

        self.label_server_username = QLabel(self.gridLayoutWidget_1)
        self.label_server_username.setObjectName("label_server_username")
        self.gridLayout.addWidget(self.label_server_username, 3, 1, 1, 1)

        self.label_server_password = QLabel(self.gridLayoutWidget_1)
        self.label_server_password.setObjectName("label_server_password")
        self.gridLayout.addWidget(self.label_server_password, 4, 1, 1, 1)

        self.label_os_type = QLabel(self.gridLayoutWidget_1)
        self.label_os_type.setObjectName("label_os_type")
        self.gridLayout.addWidget(self.label_os_type, 2, 3, 1, 1)

        self.label_server_name = QLabel(self.gridLayoutWidget_1)
        self.label_server_name.setObjectName("label_server_name")
        self.gridLayout.addWidget(self.label_server_name, 1, 3, 1, 1)

        #界面上个各个文本编辑框布局
        self.text_edit_group_name = QPlainTextEdit(self.gridLayoutWidget_1)
        self.text_edit_group_name.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_group_name.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_group_name.setObjectName("text_edit_group_name")
        self.gridLayout.addWidget(self.text_edit_group_name, 1, 2, 1, 1)

        self.text_edit_server_ip = QPlainTextEdit(self.gridLayoutWidget_1)
        self.text_edit_server_ip.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_ip.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_ip.setObjectName("text_edit_server_ip")
        self.gridLayout.addWidget(self.text_edit_server_ip, 2, 2, 1, 1)

        self.text_edit_server_username = QPlainTextEdit(self.gridLayoutWidget_1)
        self.text_edit_server_username.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_username.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_username.setObjectName("text_edit_server_username")
        self.gridLayout.addWidget(self.text_edit_server_username, 3, 2, 1, 1)

        self.text_edit_server_password = QPlainTextEdit(self.gridLayoutWidget_1)
        self.text_edit_server_password.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_password.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_password.setObjectName("text_edit_server_password")
        self.gridLayout.addWidget(self.text_edit_server_password, 4, 2, 1, 1)

        self.text_edit_os_type = QPlainTextEdit(self.gridLayoutWidget_1)
        self.text_edit_os_type.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_os_type.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_os_type.setObjectName("text_edit_os_type")
        self.gridLayout.addWidget(self.text_edit_os_type, 2, 4, 1, 1)

        self.text_edit_server_name = QPlainTextEdit(self.gridLayoutWidget_1)
        self.text_edit_server_name.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_name.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_server_name.setObjectName("text_edit_server_name")
        self.gridLayout.addWidget(self.text_edit_server_name, 1, 4, 1, 1)

        # 添加复选框[是否配置IPMI]
        self.checkbox_is_enable_ipmi = QCheckBox(self)
        self.checkbox_is_enable_ipmi.setObjectName('checkbox_is_enable_ipmi')
        self.checkbox_is_enable_ipmi.setGeometry(QRect(10, 115, 200, 20))

        # 添加栅格布局2
        self.gridLayoutWidget_2 = QWidget(self)
        self.gridLayoutWidget_2.setGeometry(QRect(10, 135, 430, 50))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")

        # 设置栅格布局2的各个标签布局
        self.label_ipmi_ip = QLabel(self.gridLayoutWidget_2)
        self.label_ipmi_ip.setObjectName("label_ipmi_ip")
        self.gridLayout_2.addWidget(self.label_ipmi_ip, 1, 1, 1, 1)

        self.label_ipmi_password = QLabel(self.gridLayoutWidget_2)
        self.label_ipmi_password.setObjectName("label_ipmi_password")
        self.gridLayout_2.addWidget(self.label_ipmi_password, 2, 1, 1, 1)

        self.label_ipmi_username = QLabel(self.gridLayoutWidget_2)
        self.label_ipmi_username.setObjectName("label_ipmi_username")
        self.gridLayout_2.addWidget(self.label_ipmi_username, 1, 3, 1, 1)

        self.text_edit_ipmi_ip = QPlainTextEdit(self.gridLayoutWidget_2)
        self.text_edit_ipmi_ip.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_ipmi_ip.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_ipmi_ip.setObjectName("text_edit_ipmi_ip")
        self.gridLayout_2.addWidget(self.text_edit_ipmi_ip, 1, 2, 1, 1)
        self.text_edit_ipmi_ip.setDisabled(True)

        self.text_edit_ipmi_password = QPlainTextEdit(self.gridLayoutWidget_2)
        self.text_edit_ipmi_password.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_ipmi_password.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_ipmi_password.setObjectName("text_edit_ipmi_password")
        self.gridLayout_2.addWidget(self.text_edit_ipmi_password, 2, 2, 1, 1)
        self.text_edit_ipmi_password.setDisabled(True)

        self.text_edit_ipmi_username = QPlainTextEdit(self.gridLayoutWidget_2)
        self.text_edit_ipmi_username.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_ipmi_username.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_ipmi_username.setObjectName("text_edit_ipmi_username")
        self.gridLayout_2.addWidget(self.text_edit_ipmi_username, 1, 4, 1, 1)
        self.text_edit_ipmi_username.setDisabled(True)

        #添加复选框[是否虚拟机]
        self.checkbox_is_virtual_machine = QCheckBox(self)
        self.checkbox_is_virtual_machine.setObjectName('checkbox_is_virtual_machine')
        self.checkbox_is_virtual_machine.setGeometry(QRect(10, 190, 200, 20))

        # 添加栅格布局3
        self.gridLayoutWidget_3 = QWidget(self)
        self.gridLayoutWidget_3.setGeometry(QRect(10, 215, 430, 50))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_2")
        self.gridLayout_3 = QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")

        # 设置栅格布局3的各个标签布局
        self.label_virtual_machine_name = QLabel(self.gridLayoutWidget_3)
        self.label_virtual_machine_name.setObjectName("label_virtual_machine_name")
        self.gridLayout_3.addWidget(self.label_virtual_machine_name, 1, 1, 1, 1)

        self.label_host_username = QLabel(self.gridLayoutWidget_3)
        self.label_host_username.setObjectName("label_host_username")
        self.gridLayout_3.addWidget(self.label_host_username, 2, 1, 1, 1)

        self.label_host_ip = QLabel(self.gridLayoutWidget_3)
        self.label_host_ip.setObjectName("label_host_ip")
        self.gridLayout_3.addWidget(self.label_host_ip, 1, 3, 1, 1)

        self.label_host_password = QLabel(self.gridLayoutWidget_3)
        self.label_host_password.setObjectName("label_host_password")
        self.gridLayout_3.addWidget(self.label_host_password, 2, 3, 1, 1)

        # 界面上个各个文本编辑框布局
        self.text_edit_virtual_machine_name = QPlainTextEdit(self.gridLayoutWidget_3)
        self.text_edit_virtual_machine_name.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_virtual_machine_name.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_virtual_machine_name.setObjectName("text_edit_virtual_machine_name")
        self.gridLayout_3.addWidget(self.text_edit_virtual_machine_name, 1, 2, 1, 1)
        self.text_edit_virtual_machine_name.setDisabled(True)

        self.text_edit_host_username = QPlainTextEdit(self.gridLayoutWidget_3)
        self.text_edit_host_username.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_host_username.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_host_username.setObjectName("text_edit_host_username")
        self.gridLayout_3.addWidget(self.text_edit_host_username, 2, 2, 1, 1)
        self.text_edit_host_username.setDisabled(True)

        self.text_edit_host_ip = QPlainTextEdit(self.gridLayoutWidget_3)
        self.text_edit_host_ip.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_host_ip.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_host_ip.setObjectName("text_edit_host_ip")
        self.gridLayout_3.addWidget(self.text_edit_host_ip, 1, 4, 1, 1)
        self.text_edit_host_ip.setDisabled(True)

        self.text_edit_host_password = QPlainTextEdit(self.gridLayoutWidget_3)
        self.text_edit_host_password.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_host_password.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_edit_host_password.setObjectName("text_edit_host_password")
        self.gridLayout_3.addWidget(self.text_edit_host_password, 2, 4, 1, 1)
        self.text_edit_host_password.setDisabled(True)

        # 添加应用按钮
        self.btn_apply = QPushButton(self)
        self.btn_apply.setGeometry(QRect(360, 270, 80, 25))
        self.btn_apply.setObjectName("button_apply")
        self.btn_apply.setDisabled(True)

        self.retranslateUi(self)  #设置静态文本

        #设置信号槽
        self.btn_apply.clicked.connect(self.clicked_btn_apply)
        self.text_edit_group_name.textChanged.connect(self.changed_text_edit)
        self.text_edit_server_ip.textChanged.connect(self.changed_text_edit)
        self.text_edit_server_username.textChanged.connect(self.changed_text_edit)
        self.text_edit_server_password.textChanged.connect(self.changed_text_edit)
        self.checkbox_is_virtual_machine.stateChanged.connect(self.changed_checkbox_is_virtual_machine)
        self.checkbox_is_enable_ipmi.stateChanged.connect(self.changed_checkbox_is_enable_ipmi)
        QMetaObject.connectSlotsByName(self)

    def changed_checkbox_is_virtual_machine(self):
        if self.checkbox_is_virtual_machine.isChecked() == True:
            self.text_edit_virtual_machine_name.setDisabled(False)
            self.text_edit_host_username.setDisabled(False)
            self.text_edit_host_ip.setDisabled(False)
            self.text_edit_host_password.setDisabled(False)
        else:
            self.text_edit_virtual_machine_name.setDisabled(True)
            self.text_edit_host_username.setDisabled(True)
            self.text_edit_host_ip.setDisabled(True)
            self.text_edit_host_password.setDisabled(True)

    def changed_checkbox_is_enable_ipmi(self):
        if self.checkbox_is_enable_ipmi.isChecked() == True:
            self.text_edit_ipmi_ip.setDisabled(False)
            self.text_edit_ipmi_username.setDisabled(False)
            self.text_edit_ipmi_password.setDisabled(False)
        else:
            self.text_edit_ipmi_ip.setDisabled(True)
            self.text_edit_ipmi_username.setDisabled(True)
            self.text_edit_ipmi_password.setDisabled(True)

    def changed_text_edit(self):
        new_group_name = self.text_edit_group_name.toPlainText()
        new_server_name = self.text_edit_server_name.toPlainText()
        new_server_ip = self.text_edit_server_ip.toPlainText()
        new_server_username = self.text_edit_server_username.toPlainText()
        new_server_password = self.text_edit_server_password.toPlainText()
        new_ipmi_ip = self.text_edit_ipmi_ip.toPlainText()
        new_ipmi_username = self.text_edit_ipmi_username.toPlainText()
        new_ipmi_password = self.text_edit_ipmi_password.toPlainText()

        flag = True
        if new_group_name == '':
            flag = False
        if new_server_name == '':
            pass
        if new_server_ip == '':
            flag = False
        if new_server_username == '':
            flag = False
        if new_server_password == '':
            flag = False
        if new_ipmi_ip == '':
            pass
        if new_ipmi_username == '':
            pass
        if new_ipmi_password == '':
            pass
        if flag:
            self.btn_apply.setDisabled(False)
        else:
            self.btn_apply.setDisabled(True)

    def clicked_btn_apply(self):
        #获取编辑框信息
        new_group_name = self.text_edit_group_name.toPlainText()
        new_server_name = self.text_edit_server_name.toPlainText()
        new_server_ip = self.text_edit_server_ip.toPlainText()
        new_server_username = self.text_edit_server_username.toPlainText()
        new_server_password = self.text_edit_server_password.toPlainText()

        new_os_type = self.text_edit_os_type.toPlainText()
        if self.checkbox_is_enable_ipmi.isChecked() == True:
            new_ipmi_flag = '1'
            new_ipmi_ip = self.text_edit_ipmi_ip.toPlainText()
            new_ipmi_username = self.text_edit_ipmi_username.toPlainText()
            new_ipmi_password = self.text_edit_ipmi_password.toPlainText()
        else:
            new_ipmi_flag = '0'
            new_ipmi_ip = ''
            new_ipmi_username = ''
            new_ipmi_password = ''

        if self.checkbox_is_virtual_machine.isChecked() == True:
            new_virtual_flag = '0'
            new_virtual_machine_name = self.text_edit_virtual_machine_name.toPlainText()
            new_host_ip = self.text_edit_host_ip.toPlainText()
            new_host_username = self.text_edit_host_username.toPlainText()
            new_host_password = self.text_edit_host_password.toPlainText()
        else:
            new_virtual_flag = '1'
            new_virtual_machine_name = ''
            new_host_ip = ''
            new_host_username = ''
            new_host_password = ''

        if new_server_ip not in SERVER_STATE_DICT.keys():
            new_server = Server()
            new_server.server_name = new_server_name
            new_server.server_ip = new_server_ip
            new_server.username = new_server_username
            new_server.password = new_server_password
            new_server.ipmi_flag = new_ipmi_flag
            new_server.ipmi_ip = new_ipmi_ip
            new_server.ipmi_username = new_ipmi_username
            new_server.ipmi_password = new_ipmi_password
            new_server.os_type = new_os_type
            new_server.virtual_flag = new_virtual_flag
            new_server.virtual_machine_name = new_virtual_machine_name
            new_server.host_ip = new_host_ip
            new_server.host_username = new_host_username
            new_server.host_password = new_host_password

            if new_group_name not in GROUP_DICT.keys():
                new_group = Group()
                new_group.addServer(new_server)
                GROUP_DICT[new_group_name] = new_group
            else:
                GROUP_DICT[new_group_name].addServer(new_server)
            save_config_from_xml_file('.\config\ServerConfig.xml')
            SERVER_STATE_DICT[new_server.server_ip] = ''
            IPMI_STATE_DICT[new_server.server_ip] = ''
            self.sin1.emit()    #发射自定义信号（配置更新后发射信号）
        self.close()

    def retranslateUi(self, Dialog):
        _translate = QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "添加服务器"))
        self.label_group_name.setText(_translate("Dialog", "*所属群组名".ljust(8)))
        self.label_server_ip.setText(_translate("Dialog", "*服务器IP地址".ljust(8)))
        self.label_server_username.setText(_translate("Dialog", "*用户名".ljust(8)))
        self.label_server_password.setText(_translate("Dialog", "*密码".ljust(8)))
        self.label_os_type.setText(_translate("Dialog", "操作系统".ljust(8)))
        self.label_server_name.setText(_translate("Dialog", "服务器名".ljust(8)))
        self.label_ipmi_ip.setText(_translate("Dialog", "IPMI地址".ljust(10)))
        self.label_ipmi_username.setText(_translate("Dialog", "IPMI用户名".ljust(10)))
        self.label_ipmi_password.setText(_translate("Dialog", "IPMI密码".ljust(10)))
        self.btn_apply.setText(_translate("Dialog", "应用"))
        self.label_virtual_machine_name.setText(_translate("Dialog", "虚拟机名".ljust(7)))
        self.label_host_ip.setText(_translate("Dialog", "宿主机IP".ljust(7)))
        self.label_host_username.setText(_translate("Dialog", "宿主机用户名".ljust(7)))
        self.label_host_password.setText(_translate("Dialog", "宿主机密码".ljust(7)))
        self.checkbox_is_enable_ipmi.setText(_translate("Dialog", "是否启用IPMI"))
        self.checkbox_is_virtual_machine.setText(_translate("Dialog", "是否虚拟机"))

class ModifyServerConfigDlg(AddServerDlg):
    def __init__(self, parent=None, selected_node_ip=None):
        #super这个用法是调用父类的构造函数
        # parent=None表示默认没有父Widget，如果指定父亲Widget，则调用之
        super(ModifyServerConfigDlg,self).__init__(parent)
        self.setObjectName("ModifyServerConfigDlg")
        self.init_ui()
        self.set_default_text_edit(selected_node_ip)

    def set_default_text_edit(self,selected_node_ip):
        for group_name in GROUP_DICT:
            for server_ip in GROUP_DICT[group_name].server_dict:
                if selected_node_ip == server_ip:
                    server = GROUP_DICT[group_name].server_dict[server_ip]
                    self.text_edit_group_name.setPlainText(group_name)
                    self.text_edit_group_name.setDisabled(True)
                    self.text_edit_server_name.setPlainText(server.server_name)
                    self.text_edit_server_ip.setPlainText(server.server_ip)
                    self.text_edit_server_ip.setDisabled(True)
                    self.text_edit_server_username.setPlainText(server.username)
                    self.text_edit_server_password.setPlainText(server.password)
                    self.text_edit_os_type.setPlainText(server.os_type)
                    if server.ipmi_flag == '1':
                        self.checkbox_is_enable_ipmi.setChecked(True)
                        self.text_edit_ipmi_ip.setPlainText(server.ipmi_ip)
                        self.text_edit_ipmi_username.setPlainText(server.ipmi_username)
                        self.text_edit_ipmi_password.setPlainText(server.ipmi_password)
                    else:
                        self.checkbox_is_enable_ipmi.setChecked(False)
                    if server.virtual_flag == '0':
                        self.checkbox_is_virtual_machine.setChecked(True)
                        self.text_edit_virtual_machine_name.setPlainText(server.virtual_machine_name)
                        self.text_edit_host_ip.setPlainText(server.host_ip)
                        self.text_edit_host_username.setPlainText(server.host_username)
                        self.text_edit_host_password.setPlainText(server.host_password)
                    else:
                        self.checkbox_is_virtual_machine.setChecked(False)

    def clicked_btn_apply(self):
        #获取编辑框信息
        new_group_name = self.text_edit_group_name.toPlainText()
        new_server_name = self.text_edit_server_name.toPlainText()
        new_server_ip = self.text_edit_server_ip.toPlainText()
        new_server_username = self.text_edit_server_username.toPlainText()
        new_server_password = self.text_edit_server_password.toPlainText()
        new_os_type = self.text_edit_os_type.toPlainText()
        if self.checkbox_is_enable_ipmi.isChecked() == True:
            new_ipmi_flag = '1'
            new_ipmi_ip = self.text_edit_ipmi_ip.toPlainText()
            new_ipmi_username = self.text_edit_ipmi_username.toPlainText()
            new_ipmi_password = self.text_edit_ipmi_password.toPlainText()
        else:
            new_ipmi_flag = '0'
            new_ipmi_ip = ''
            new_ipmi_username = ''
            new_ipmi_password = ''
        if self.checkbox_is_virtual_machine.isChecked() == True:
            new_virtual_flag = '0'
            new_virtual_machine_name = self.text_edit_virtual_machine_name.toPlainText()
            new_host_ip = self.text_edit_host_ip.toPlainText()
            new_host_username = self.text_edit_host_username.toPlainText()
            new_host_password = self.text_edit_host_password.toPlainText()
        else:
            new_virtual_flag = '1'
            new_virtual_machine_name = ''
            new_host_ip = ''
            new_host_username = ''
            new_host_password = ''
        new_server = Server()
        new_server.server_name = new_server_name
        new_server.server_ip = new_server_ip
        new_server.username = new_server_username
        new_server.password = new_server_password
        new_server.ipmi_flag = new_ipmi_flag
        new_server.ipmi_ip = new_ipmi_ip
        new_server.ipmi_username = new_ipmi_username
        new_server.ipmi_password = new_ipmi_password
        new_server.os_type = new_os_type
        new_server.virtual_flag = new_virtual_flag
        new_server.virtual_machine_name = new_virtual_machine_name
        new_server.host_ip = new_host_ip
        new_server.host_username = new_host_username
        new_server.host_password = new_host_password
        if new_group_name not in GROUP_DICT.keys():
            new_group = Group()
            new_group.addServer(new_server)
            GROUP_DICT[new_group_name] = new_group
        else:
            GROUP_DICT[new_group_name].addServer(new_server)
        save_config_from_xml_file('.\config\ServerConfig.xml')
        SERVER_STATE_DICT[new_server.server_ip] = ''
        IPMI_STATE_DICT[new_server.server_ip] = ''
        self.sin1.emit()    #发射自定义信号（配置更新后发射信号）
        self.close()