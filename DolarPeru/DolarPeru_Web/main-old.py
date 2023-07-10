import os, json, platform, sys
from flask import Flask, redirect, url_for, render_template, request
from google.cloud import storage


def which_system():
    systems = [
        {"name": "GFT-Tablet", "root_path": r"C:\pythonCode"},
        {"name": "raspberrypi", "root_path": r"/home/pi/pythonCode"},
        {"name": "laptop", "root_path": r"C:\pythonCode"},
        {"name": "Ubuntu-gft", "root_path": "/home/gabriel/pythonCode"},
        {"name": "Google Cloud App Engine", "root_path": "/home/gabfre/pythonCode"},
    ]
    for system in systems:
        if system["name"] in platform.node():
            return system["name"], system["root_path"]
    return systems[-1]["name"], systems[-1]["root_path"]


def get_data_from_bucket(filename):
    # Access Google Cloud Storage Bucket
    if SYSTEM != "Google Cloud App Engine":
        client = storage.Client.from_service_account_json(
            json_credentials_path=GCLOUD_KEYS
        )
    else:
        client = storage.Client()
    bucket = client.get_bucket(GCLOUD_BUCKET)
    file_in_bucket = bucket.blob("/DolarPeru_data/" + filename)
    data = json.loads(file_in_bucket.download_as_string().decode("utf-8"))
    return data


def get_data_from_file(filename):
    with open("c:/pythonCode/DolarPeru_data/" + filename, "r") as file:
        data = json.loads(file.read())
    return data


def split_in_two(details):
    return details[: len(details) // 2], details[len(details) // 2 :]


SYSTEM, ROOT_PATH = which_system()
GCLOUD_KEYS = os.path.join(ROOT_PATH, "gcloud_keys.json")
GCLOUD_BUCKET = "data-bucket-gft"  # testing = 'data-bucket-gft-devops' | production = 'data-bucket-gft'

app = Flask(__name__)


@app.route("/")
@app.route("/venta")
def venta():
    data = get_data_from_bucket("WEB_Venta.json")
    details1, details2 = split_in_two(data["details"])
    return render_template(
        "venta.html", head=data["head"], details1=details1, details2=details2
    )


@app.route("/compra")
def compra():
    data = get_data_from_bucket("WEB_Compra.json")
    details1, details2 = split_in_two(data["details"])
    return render_template(
        "compra.html", head=data["head"], details1=details1, details2=details2
    )


@app.route("/stats")
def stats():
    data = get_data_from_bucket("stats.json")
    return render_template("stats.html", meta=data["Meta"], results=data["Results"])


@app.route("/fintech/<path:id>")
def fintech(id):
    data = get_data_from_file("WEB_" + id + ".json")
    return render_template(
        "fintech.html",
        id=id,
        datos=data["datos"],
        ultima=data["cotizaciones"][-1],
        antiguas=data["cotizaciones"][:-1],
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
