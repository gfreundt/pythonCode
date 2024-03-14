import subprocess
from datetime import datetime as dt
import time

for i in range(5):
    subprocess.call(["python", "updater.py"])
    print(f"\n*** MAJOR RESET #{i+1} [{dt.now().strftime('%H:%M:%S')}]")
    time.sleep(5)
