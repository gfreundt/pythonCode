import os, csv
from flask import Flask, render_template, request

app = Flask(__name__)


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
def status():
    data = [
        {"elapsed": "34:34:34", "timeout": "3:55:12", "last_write": "12:12:00"},
    ]
    data1 = {
        "active": True,
        "process": "Procesassdda",
        "cur_rec": 76,
        "tot_recs": 5000,
        "complet": "8.6%",
        "status": "ACTIVE",
        "rate": "6.7",
        "eta": "05-06-24 06:44:12",
    }
    data2 = {
        "active": False,
        "process": "Procesassdda",
        "cur_rec": 76,
        "tot_recs": 5000,
        "complet": "8.6%",
        "status": "ACTIVE",
        "rate": "16.3",
        "eta": "05-06-24 06:44:12",
    }
    data.append(data1)
    data.append(data2)
    return render_template("status.html", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
