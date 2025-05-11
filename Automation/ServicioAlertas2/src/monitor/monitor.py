from flask import Flask, render_template, jsonify
import threading
from copy import deepcopy as copy
from pprint import pprint


class Dashboard:
    def __init__(self):
        self.app = Flask(__name__, template_folder="../templates")
        self.data_lock = threading.Lock()

        # Define routes
        self.app.add_url_rule("/", "dashboard", self.dashboard)
        self.app.add_url_rule("/data", "get_data", self.get_data)

        self.set_initial_data()

    def log(self, **kwargs):

        if "general_status" in kwargs:
            self.data["top_right"] = kwargs["general_status"]
        if "actions" in kwargs:
            self.data["bottom_left"].append(kwargs["actions"])
            if len(self.data["bottom_left"]) > 4:
                self.data["bottom_left"].pop(0)
        if "card" in kwargs:
            for field in kwargs:
                if field == "card":
                    continue
                self.data["cards"][kwargs["card"]][field] = kwargs[field]
        if "info1" in kwargs:
            self.data["bottom_right"].append(kwargs["info1"])

    def set_initial_data(self):
        empty_card = {
            "title": "Sin Informacion",
            "progress": 0,
            "msg": [],
            "status": 0,
            "text": ".",
            "lastUpdate": "2000-01-01",
        }
        self.data = {
            "top_left": "No Pasa Nada Dashboard",
            "top_right": "RUNNING",
            "cards": [copy(empty_card) for _ in range(12)],
            "bottom_left": [""],
            "bottom_right": [""],
        }

    def dashboard(self):
        return render_template("dashboard.html", data=self.data)

    def get_data(self):
        with self.data_lock:
            return jsonify(self.data)

    def run(self, debug=False):
        self.app.run(debug=debug, use_reloader=False, threaded=True, port=7000)

    def run_in_background(self):
        flask_thread = threading.Thread(target=self.run, daemon=True)
        flask_thread.start()
        return flask_thread


if __name__ == "__main__":
    app_instance = Dashboard()
    app_instance.run(debug=True)
