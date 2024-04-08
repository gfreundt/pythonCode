import os, csv, time, signal
from datetime import datetime as dt
import platform
import socket
from gft_utils import ChromeUtils
import pyautogui
from random import randrange

# import and activate Flask, change logging level to reduce messages
from flask import Flask, render_template, request

app = Flask(__name__)


# define all api endpoints and launcher
@app.route("/")
def root():
    print("root!")


@app.route("/status")
def status():
    return render_template("status.html", data=MONITOR.api_data)


"""@app.route("/killemall", methods=["POST"])
def killemall():
    MONITOR.kill_em_all = True
    return render_template("status.html", data=MONITOR.api_data)"""


@app.route("/panic", methods=["POST"])
def panic():
    os.kill(os.getpid(), getattr(signal, "SIGKILL", signal.SIGTERM))


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", data=MONITOR.dash_data)


def stats_view(MONITOR):
    # wait until port assigned by a different thread
    while not MONITOR._port:
        time.sleep(2)

    # open browser on status page
    webdriver = ChromeUtils().init_driver(
        headless=False, verbose=False, window_size=(900, 310)
    )
    if pyautogui.size()[0] == 3840:
        posx, posy = (1670, 1080)
    elif pyautogui.size()[0] == 1920:
        posx, posy = (700, 420)
    webdriver.set_window_position(posx, posy, windowHandle="current")
    webdriver.get(url=f"http://{MONITOR._myip}:{MONITOR._port}/status")

    # forever loop refreshing status page
    while True:
        time.sleep(3)
        webdriver.refresh()


def assign_port():
    _devices = {"power": 12500, "salita-tv": 13500, "rpi": 14500}
    return _devices.get(platform.node().lower(), 21000) + randrange(100)


def main(monitor, LOG):
    global MONITOR
    MONITOR = monitor
    MONITOR._myip = socket.gethostbyname(socket.gethostname())
    MONITOR._port = assign_port()
    print(f"Status: {MONITOR._myip}:{MONITOR._port}/status")
    LOG.info(f"Port: {MONITOR._port}")

    app.run(host=MONITOR._myip, port=MONITOR._port, debug=False)
