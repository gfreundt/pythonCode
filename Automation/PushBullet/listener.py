import websocket
import requests
import time
import subprocess
import sys
import platform
import os


def get_key():
    with open("pushbullet_key.txt", mode="r") as file:
        return file.read().strip()


def check_system_path():
    if "Windows" in platform.uname().system:
        root = os.path.join(r"d:\pythonCode")
        ext = "PC1"
    else:
        root = os.path.join("/home/gfreundt/pythonCode")
        ext = "RP1"
    return os.path.join(root, "Automation", "PushBullet"), ext


def take_action(message, extension):
    if extension in message:
        if "stop internet" in message:
            os.chdir(path)
            subprocess.run(["python", "switch-internet.py", "OFF"])
            return "continue"
        elif "start internet" in message:
            os.chdir(path)
            subprocess.run(["python", "switch-internet.py", "ON"])
            return "continue"
        elif "quit" in message:
            return "stop"


def wait_for_message(token, time_limit, path, extension):
    uri = f"wss://stream.pushbullet.com/websocket/{token}"
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
                after_action = take_action(
                    message=message.lower(), path=path, extension=extension
                )
                if after_action == "stop":
                    ws.close()
                    return
        else:
            ws.close()
            return


time_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
path, ext = check_system_path()
wait_for_message(token=get_key(), time_limit=time_limit, path=path, extension=ext)
