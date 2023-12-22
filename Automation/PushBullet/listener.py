import websocket
import requests
import time
import subprocess
import sys


def wait_for_message(token, time_limit):
    uri = f"wss://stream.pushbullet.com/websocket/{at}"
    ws = websocket.WebSocket()
    ws.connect(uri)
    start = time.time()
    while True:
        if time.time() - start < time_limit or time_limit == 0:
            receive = ws.recv()
            if "tickle" in receive:
                print("notification!")
                url = "https://api.pushbullet.com/v2/pushes"
                header = {"Access-Token": token}
                params = {"modified_after": time.time() - 30}
                x = requests.get(url, headers=header, params=params)
                r = x.json()["pushes"][0]
                print(
                    f"Time: {r['created']} - Text: {r['body']} - Unique ID: {r['guid']}"
                )
                if r["body"].strip() == "notepad":
                    subprocess.run(
                        [
                            r"C:\pythonCodePlus\Resources\Scripts\Push2RunAutomation\toip.bat"
                        ]
                    )
                elif r["body"].strip() == "quit":
                    ws.close()
                    quit()
        else:
            ws.close()
            return


at = "o.hb6GkzmwgludKtUOhv2hyeGz3kadMstt"
time_limit = int(sys.argv[1]) if len(sys.argv) > 1 else 120

wait_for_message(token=at, time_limit=time_limit)
