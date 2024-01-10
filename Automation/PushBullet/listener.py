import websocket
import requests
import time
import subprocess
import platform
import os
import json
from datetime import datetime as dt


class PushBullet:
    def __init__(self):
        # path and platform code depends if service running on Windows or Raspberry
        self.path, self.platf = self.check_system_path()
        # get secret token from local file, created request header
        with open(os.path.join(self.path, "pushbullet_key.txt"), mode="r") as file:
            self.token = file.read().strip()
            self.header = {"Access-Token": self.token}
        # get list of trigger phrases, corresponding actions and platforms
        with open(os.path.join(self.path, "monitored_events.json"), mode="r") as file:
            self.events = json.load(file)["events"]
        # list of attended instructions (empty to begin with)
        self.attended_instructions = []

    def check_system_path(self):
        if "Windows" in platform.uname().system:
            root = os.path.join(r"d:\pythonCode")
            platf = "pc1"
        else:
            root = os.path.join("/home/gfreundt/pythonCode")
            platf = "rp1"
        return os.path.join(root, "Automation", "PushBullet"), platf

    def listener(self):
        # run specific action depending on message received
        def take_action(instruction):
            # if no specific platform defined, default to rp1
            if not "rp1" in instruction and not "pc1" in instruction:
                instruction += " rp1"
            for event in self.events:
                if (
                    event["trigger_phrase"] in instruction
                    and self.platf in instruction
                    and self.platf in event["platforms"]
                ):
                    self.stdout(f"Instruction received ({event['trigger_phrase']})")
                    self.send_push(
                        title="Action Requested",
                        message=f"[{dt.now().strftime('%H:%M:%S')}] {event['trigger_phrase']}",
                    )
                    # change directory
                    if event.get("change_directory"):
                        os.chdir(self.path)
                    # execute os-level code
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
                        self.send_push(
                            title="Action Success",
                            message=f"[{dt.now().strftime('%H:%M:%S')}] {_msg}",
                        )
                    # continue/stop listener
                    return "continue" if event["continue"] else "stop"

        # connect to PushBullet service
        uri = f"wss://stream.pushbullet.com/websocket/{self.token}"
        reconnect_attempts = 1
        while reconnect_attempts <= 5:
            try:
                self.stdout(
                    f"Connecting to PushBullet Websocket - Attempt {reconnect_attempts}/5."
                )
                socket = websocket.WebSocket()
                socket.connect(uri)
                # reset reconnection attempts counter
                reconnect_attempts = 0
                self.stdout("Connected. Listening for Instructions.")
                # permanent listening until asked to quit or time exceeded
                while True:
                    time.sleep(1)
                    receive = socket.recv()
                    if "tickle" in receive:
                        url = "https://api.pushbullet.com/v2/pushes"
                        params = {"modified_after": time.time() - 5}
                        response = requests.get(url, headers=self.header, params=params)
                        if (
                            response.json()["pushes"][-1]["guid"]
                            not in self.attended_instructions
                        ):
                            instruction = (
                                response.json()["pushes"][-1]["body"].strip().lower()
                            )
                            after_action = take_action(instruction=instruction)
                            if after_action == "stop":
                                socket.close()
                                return
                            self.attended_instructions.append(
                                response.json()["pushes"][-1]["guid"]
                            )

            except KeyboardInterrupt:
                quit()
            except:
                # wait before attempting reconnect
                self.stdout("Connection Error... Waiting 30 seconds to reconnect.")
                time.sleep(30)
                reconnect_attempts += 1

    def send_push(self, title, message):
        uri = "https://api.pushbullet.com/v2/pushes"
        params = {"type": "note", "title": title, "body": message}
        _ = requests.post(uri, headers=self.header, data=params)

    def get_devices(self):
        url = "https://api.pushbullet.com/v2/devices"
        response = requests.get(url, headers=self.header)
        return {i["nickname"]: i["iden"] for i in response.json()["devices"]}

    def stdout(self, message):
        print(f"[{dt.now().strftime('%H:%M:%S')}] {message}")


def main():
    pb = PushBullet()
    pb.listener()


main()
