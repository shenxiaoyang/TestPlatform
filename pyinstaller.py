# -*- coding:utf-8 -*-
import os
cmd1 = r'C:\Users\TEST001\AppData\Local\Programs\Python\Python35\Scripts\pyinstaller.exe' \
      r' -F -w C:\Users\TEST001\PycharmProjects\TestPlatform\TestPlatform.py'
os.system(cmd1)

cmd2 = r'xcopy C:\Users\TEST001\PycharmProjects\TestPlatform\dist\TestPlatform.exe ' \
       r'C:\Users\TEST001\PycharmProjects\TestPlatform\TestPlatform.exe /y'
os.system(cmd2)

cmd3 = r'start C:\Users\TEST001\PycharmProjects\TestPlatform\TestPlatform.exe'
os.system(cmd3)