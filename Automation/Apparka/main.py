import subprocess
from datetime import datetime as dt
import time

for i in range(3):
    subprocess.call(["python", "updater.py"])
    time.sleep(10)
