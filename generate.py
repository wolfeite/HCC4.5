import os
# os.system("chcp 65001")
# os.system('arp -a > temp.txt')
# os.system('ping 8.8.8.8 -t')
# os.system('ping 8.8.8.8')
# print(os.popen('arp -a > temp.txt').read())

from libs.analyser.Config import Modules
f = Modules(("data", "builder.json"))
f.generate_spec()
os.system('pyinstaller index_debug.spec')
os.system('pyinstaller index.spec')
