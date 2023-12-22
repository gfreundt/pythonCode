import websocket
import requests
import time
import subprocess
import sys
import platform
import os


def check_system_path():
    if "Windows" in platform.uname().system:
        root = os.path.join(r"d:\pythonCode")
    else:
        root = os.path.join("~/pythonCode")

    return os.path.join(root, "Automation", "PushBullet")


def wait_for_message(token, time_limit, path):
    uri = f"wss://stream.pushbullet.com/websocket/{at}"
    ws = websocket.WebSocket()
    ws.connect(uri)
    start = time.time()
    while True:
        if time.time() - start < time_limit or time_limit == 0:
            receive = ws.recv()
            if "tickle" in receive:
                url = "https://api.pushbullet.com/v2/pushes"
                header = {"Access-Token": token}
                params = {"modified_after": time.time() - 5}
                response = requests.get(url, headers=header, params=params)
                message = response.json()["pushes"][-1]["body"].strip()
                if "stop internet" in message:
                    subprocess.run([os.path.join(path, ""), "OFF"])
                if "start internet" in message:
                    subprocess.run([os.path.join(path, ""), "ON"])
                elif "quit" in message:
                    ws.close()
                    quit()
        else:
            ws.close()
            return


at = "o.hb6GkzmwgludKtUOhv2hyeGz3kadMstt"
time_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 120
path = check_system_path()
wait_for_message(token=at, time_limit=time_limit, path=path)
