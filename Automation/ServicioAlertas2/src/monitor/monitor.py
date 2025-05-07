from flask import Flask, render_template, jsonify
import threading


class Dashboard:
    def __init__(self):
        self.app = Flask(__name__, template_folder="../templates")
        self.data = {
            "top_left": "Initializing...",
            "top_right": "Waiting...",
            "cards": [f"Card {i+1}: Idle" for i in range(12)],
            "bottom_left": ["Blank"] * 4,
            "bottom_right": "System normal",
        }
        self.data_lock = threading.Lock()

        # Define routes
        self.app.add_url_rule("/", "dashboard", self.dashboard)
        self.app.add_url_rule("/data", "get_data", self.get_data)

        self.set_initial_data()

    def log(self, **kwargs):

        if "status" in kwargs:
            self.data["top_right"] = kwargs["status"]
        if "actions" in kwargs:
            self.data["bottom_left"].append(kwargs["actions"])
            if len(self.data["bottom_left"]) > 4:
                self.data["bottom_left"].pop(0)

    def set_initial_data(self):
        self.data = {
            "top_left": "No Pasa Nada Dashboard",
            "top_right": "Starting",
            "cards": [f"Proceso {i+1}: Sin Informacion" for i in range(12)],
            "bottom_left": "Pendiente",
            "bottom_right": "Pendiente",
        }

    def dashboard(self):
        return render_template("dashboard.html")

    def get_data(self):
        with self.data_lock:
            return jsonify(self.data)

    def run(self):
        self.app.run(debug=False, use_reloader=False, threaded=True, port=7000)

    def run_in_background(self):
        flask_thread = threading.Thread(target=self.run, daemon=True)
        flask_thread.start()
        return flask_thread


if __name__ == "__main__":
    app_instance = Dashboard()
    app_instance.run(debug=True)
