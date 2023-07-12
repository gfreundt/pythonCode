import json
import os
import platform
from datetime import datetime as dt
from datetime import timedelta as td
from flask import Flask, render_template, redirect, request, url_for

app = Flask(__name__)


# Homepage
@app.route("/")
@app.route("/loaded")
def loaded():
    return render_template("loaded.html", data=update_html_data())


# Landing page only receives data from JS
@app.route("/processAction", methods=["POST"])
def update():
    result = json.loads(request.get_json())
    table, action, row = result[0], result[1], result[2]
    print(result)

    if action == "e":
        print("dedd")
        return "oops"  # render_template("properties.html", defaults=form_defaults("xyz.jpg"))

    return result

    position = int(result[2:])
    # Active --> Inactive
    if result[1] == "d":
        for i, item in enumerate(media):
            if item["active"] and item["position"] == position:
                media[i]["active"] = False
    # Inactive --> Active
    elif result[1] == "a":
        for i, item in enumerate(media):
            if not item["active"] and item["position"] == position:
                media[i]["active"] = True
    # Unload Media
    elif result[1] == "u":
        pass
    # Complete action by recalculating positions for active and inactive
    active = [i for i in media if i["active"]]
    inactive = [i for i in media if not i["active"]]
    for n, _ in enumerate(active):
        active[n]["position"] = n
    for n, _ in enumerate(inactive):
        inactive[n]["position"] = n
    test = active + inactive
    # Save JSON file
    with open(".\static\json\storyboard_active.json", mode="w") as json_file:
        json.dump({"loaded_media": active + inactive}, json_file)

    return result


@app.route("/unloaded")
def unloaded():
    return render_template("unloaded.html", data=update_html_data())


@app.route("/unsupported")
def unsupported():
    return render_template("unsupported.html", data=update_html_data())


@app.route("/properties", methods=["POST", "GET"])
def properties():
    if request.method == "POST":
        form_data = []
        for d in [
            "name",
            "duration",
            "start_date",
            "start_time",
            "end_date",
            "end_time",
        ]:
            form_data.append(request.form[d])
        print(form_data)
        return redirect(url_for("loaded"))
    else:
        filename = os.path.join(STATIC_DIR, "media", "xyz.jpg")
        return render_template(
            "properties.html",
            data=load_storyboard(),
            defaults=form_defaults(filename),
            media=filename.split("\\")[-1],
        )


def load_storyboard():
    """Load JSON file that holds all media information"""
    with open(
        os.path.join(STATIC_DIR, "json", "storyboard_active_new.json"),
        mode="r",
    ) as json_file:
        storyboard = json.load(json_file)
        return storyboard["active"], storyboard["inactive"]


def update_html_data():
    active_media, inactive_media = load_storyboard()
    loaded_media_filenames = [i["file_name"] for i in (active_media + inactive_media)]
    unloaded = [
        i
        for i in os.listdir(os.path.join(STATIC_DIR, "media"))
        if i not in loaded_media_filenames
    ]
    return {"active": active_media, "inactive": inactive_media, "unloaded": unloaded}


def form_defaults(filename):
    print(filename)
    """
    cap = cv2.VideoCapture(filename)
    fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    d = int(frame_count * 10 / fps) / 10
    """
    d = 10

    return {
        "name": filename.split(".")[1],
        "duration": d,
        "start_date": dt.strftime(dt.now(), "%Y-%m-%d"),
        "start_time": dt.strftime(dt.now(), "%H:%M"),
        "end_date": dt.strftime(dt.now() + td(days=1), "%Y-%m-%d"),
        "end_time": dt.strftime(dt.now(), "%H:%M"),
    }


def main():

    # setup
    global STATIC_DIR
    directories = {
        "Windows": r"C:\pythonCode\rollerAds\player\static",
        "Linux": r"/home/pi/pythonCode/rollerAds/player/static",
    }
    STATIC_DIR = directories[platform.system()]

    # run server
    app.run(host="0.0.0.0", debug=True)
    print("Updater Running")


main()
