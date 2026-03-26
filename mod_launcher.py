from subprocess import Popen
import os
import time

LAUNCH_WITH_SOLDAT = False
SOLDAT_EXECUTABLE_DIR = r"C:\Soldat\soldat.exe"

if LAUNCH_WITH_SOLDAT:
    Popen(SOLDAT_EXECUTABLE_DIR)
    time.sleep(3)
os.system("python main.py")
