# -*- coding: utf-8 -*-
import sys
import logging.config
import os
import traceback
from PyQt5 import  QtWidgets

#配置日志记录器，从日志配置文件中读取配置
#注意main日志记录器初始化需要放在外部模块加载之前，因为外部模块加载的时候会初始化子模块日志记录器
if not os.path.exists(r'.\log'):
    os.makedirs(r'.\log')
logging.config.fileConfig(r'.\config\logger.conf')
logger = logging.getLogger('root.main')

#加载自定义模块
from TestPlatformUI import MainWindows,read_config_from_xml_file

if __name__ == "__main__":
    try:
        read_config_from_xml_file('.\config\ServerConfig.xml')
        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindows()
        logging.debug('打开主窗口')
        main_window.show()
        sys.exit(app.exec_())
    except BaseException as exec_:
        print(traceback.print_exc())

