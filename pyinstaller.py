# -*- coding: utf-8 -*-
import os
cmd1 = r'C:\Users\TEST001\AppData\Local\Programs\Python\Python35\Scripts\pyinstaller.exe' \
      r' -F C:\Users\TEST001\PycharmProjects\TestPlatform_github\TestPlatformMain.py'
os.system(cmd1)

cmd2 = r'xcopy C:\Users\TEST001\PycharmProjects\TestPlatform_github\dist\TestPlatformMain.exe ' \
       r'C:\Users\TEST001\PycharmProjects\TestPlatform_github /y'
os.system(cmd2)

cmd3 = r'start C:\Users\TEST001\PycharmProjects\TestPlatform_github\TestPlatformMain.exe'
os.system(cmd3)