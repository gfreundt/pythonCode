import os, time, signal
import platform
import socket
from gft_utils import ChromeUtils
from random import randrange
import logging
import pyautogui

# import and activate Flask, change logging level to reduce messages
from flask import Flask, render_template

app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


# define all api endpoints and launcher
@app.route("/")
def root():
    print("root!")


@app.route("/status")
def status():
    return render_template("status.html", data=MONITOR.api_data)


@app.route("/killemall", methods=["POST"])
def killemall():
    MONITOR.kill_em_all = True
    LOG.info("API > Soft Kill Button Pressed.")


@app.route("/panic", methods=["POST"])
def panic():
    LOG.info("API > Hard Kill Button (Panic) Pressed.")
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
        headless=False, verbose=False, window_size=(1000, 310)
    )
    if pyautogui.size()[0] == 3840:
        posx, posy = (1540, 1080)
    elif pyautogui.size()[0] == 1920:
        posx, posy = (600, 420)
    webdriver.set_window_position(posx, posy, windowHandle="current")
    webdriver.get(url=f"http://{MONITOR._myip}:{MONITOR._port}/status")

    # forever loop refreshing status page until flag is turned on
    while not (MONITOR.timeout_flag or MONITOR.updaters_end_flag):
        time.sleep(3)
        webdriver.refresh()

    # close status browser
    webdriver.quit()


def assign_port():
    _devices = {"power": 12500, "salita-tv": 13500, "rpi": 14500}
    return _devices.get(platform.node().lower(), 21000) + randrange(999)


def main(monitor, log):
    global MONITOR, LOG
    MONITOR, LOG = monitor, log
    LOG.info("API > Begin.")
    MONITOR._myip = socket.gethostbyname(socket.gethostname())
    MONITOR._port = assign_port()
    print(f"For status: http://{MONITOR._myip}:{MONITOR._port}/status")
    LOG.info(f"For status: http://{MONITOR._myip}:{MONITOR._port}/status")

    app.run(host=MONITOR._myip, port=MONITOR._port, debug=False)
