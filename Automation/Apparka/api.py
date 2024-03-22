import os, csv
from flask import Flask, render_template, request

app = Flask(__name__)


class Api:

    def __init__(self) -> None:
        self.DASHBOARD_NAME = os.path.join(os.getcwd(), "data", "dashboard.csv")

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/rtec", methods=["GET", "POST"])
    def rtec():
        if request.method == "POST":
            dni = request.form.get("dni")
            print(dni)
            # return Brevete().run_single_update(dni=dni)
        return render_template("rtec.html")

    @app.route("/dashboard")
    def dashboard():
        with open(self.DASHBOARD_NAME, "r") as file:
            dashboard = [i for i in csv.reader(file, delimiter="|", quotechar="'")]
            print(dashboard[0])
        return render_template("dashboard.html", data=dashboard[0])

    @app.route("/status")
    def status(data):
        print(data)
        return render_template("status.html", data=data)

    def run(self):
        app.run(host="0.0.0.0", port=8000, debug=True)


if __name__ == "__main__":
    api = Api()
    api.run(data="")
