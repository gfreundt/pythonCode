from updater_dev import Brevete

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
        return Brevete().run_single_update(dni=dni)
    return render_template("rtec.html")


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=8000, debug=True)
