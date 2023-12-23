import websocket
import requests
import time
import subprocess
import sys
import platform
import os
import json


class PushBullet:
    def __init__(self):
        # path and extension code depends if service running on Windows or Raspberry
        self.path, self.extension = self.check_system_path()
        # get secret token from local file, created request header
        with open(os.path.join(self.path, "pushbullet_key.txt"), mode="r") as file:
            self.token = file.read().strip()
            self.header = {"Access-Token": self.token}
        # get list of trigger phrases, corresponding actions and platforms
        with open(os.path.join(self.path, "monitored_events.json"), mode="r") as file:
            self.events = json.load(file)["events"]

    def check_system_path(self):
        if "Windows" in platform.uname().system:
            root = os.path.join(r"d:\pythonCode")
            extension = "pc1"
        else:
            root = os.path.join("/home/gfreundt/pythonCode")
            extension = "rp1"
        return os.path.join(root, "Automation", "PushBullet"), extension

    def listener(self, time_limit):
        # run specific action depending on message received
        def take_action(instruction):
            print("1  ", instruction)
            for event in self.events:
                print("2  ", event)
                print("3  ", self.extension)
                if (
                    event["trigger_phrase"] in instruction
                    and self.extension in event["platforms"]
                ):
                    # change directory
                    if event.get("change_directory"):
                        os.chdir(self.path)
                    # execute system-level code
                    if event.get("action"):
                        process = subprocess.run(
                            event["action"], capture_output=True, check=False
                        )
                        # respond with success/failure message
                        _msg = (
                            event["response_on_success"]
                            if process.returncode == 0
                            else event["response_on_failure"]
                        )
                        self.send_push(_msg)
                    # continue/stop listener
                    return "continue" if event["continue"] else "stop"

        def take_action2(message):
            if self.extension in message:
                if "stop internet" in message:
                    os.chdir(self.path)
                    process = subprocess.run(
                        ["python", "switch-internet.py", "OFF"],
                        capture_output=True,
                        check=False,
                    )
                    if process.returncode == 0:
                        self.send_push("* Process Succesful *")
                    else:
                        self.send_push("Error!")
                    return "continue"
                elif "start internet" in message:
                    os.chdir(self.path)
                    subprocess.run(
                        ["python", "switch-internet.py", "ON"],
                        capture_output=True,
                        check=False,
                    )
                    if process.returncode == 0:
                        self.send_push("* Process Succesful *")
                    else:
                        self.send_push("Error!")
                    return "continue"
                elif "sleep" in message:
                    socket.close()
                    subprocess.run(
                        ["rundll32.exe", "powrprof.dll", "SetSuspendState", "Sleep"]
                    )
                    return "stop"
                elif "quit" in message:
                    self.send_push("* Listener Stopped *")
                    return "stop"

        # connect to PushBullet service
        uri = f"wss://stream.pushbullet.com/websocket/{self.token}"
        socket = websocket.WebSocket()
        socket.connect(uri)
        # permanent listening until asked to quit or time exceeded
        start = time.time()
        while True:
            if time.time() - start < time_limit or time_limit == 0:
                receive = socket.recv()
                if "tickle" in receive:
                    url = "https://api.pushbullet.com/v2/pushes"
                    params = {"modified_after": time.time() - 5}
                    response = requests.get(url, headers=self.header, params=params)
                    instruction = response.json()["pushes"][-1]["body"].strip().lower()
                    after_action = take_action(instruction=instruction)
                    if after_action == "stop":
                        socket.close()
                        return
            else:
                socket.close()
                return

    def send_push(self, message):
        uri = "https://api.pushbullet.com/v2/pushes"
        params = {"type": "note", "title": "Action Requested", "body": message}
        _ = requests.post(uri, headers=self.header, data=params)

    def get_devices(self):
        url = "https://api.pushbullet.com/v2/devices"
        response = requests.get(url, headers=self.header)
        return {i["nickname"]: i["iden"] for i in response.json()["devices"]}


def main():
    pb = PushBullet()
    time_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    pb.listener(time_limit=time_limit)


main()
