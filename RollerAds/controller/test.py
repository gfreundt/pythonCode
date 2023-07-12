import json, time
import os
import platform
import shutil
from datetime import datetime as dt
from datetime import timedelta
import uuid
import filetype
import threading
import cv2

from tables import Table

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.popup import Popup
from kivy.clock import mainthread

from kivymd.app import MDApp
from kivymd.uix.pickers import MDDatePicker

# TODO: thumbnail creation update
# TODO: save new storyboard.json with updated info
# TODO: confirmation for unload
# TODO: dashboard: total time, media time breakdown, etc
# TODO: video thumbnails
# TODO: preview storyboard
# TODO: advanced scheduling


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.interrupt = False

    def play(self):
        all_active_media = [i["playback"] for i in MAIN.active_data]
        while True:
            for play_this in all_active_media:
                if play_this["type"] == "Video":
                    media = cv2.VideoCapture(
                        os.path.join(MAIN.MEDIA_LOCATION, play_this["file_name"])
                    )
                    fps = int(media.get(cv2.CAP_PROP_FPS))
                    while media.isOpened():
                        ret, frame = media.read()
                        if ret:
                            time.sleep(1 / fps)
                            cv2.imshow("frame", frame)
                            if cv2.waitKey(1) & 0xFF == 27:
                                cv2.destroyAllWindows()
                                return
                        else:
                            break
                else:
                    media = cv2.imread(
                        os.path.join(MAIN.MEDIA_LOCATION, play_this["file_name"])
                    )
                    cv2.imshow("media", media)
                    start = dt.now()
                    while dt.now() - start < timedelta(seconds=play_this["duration"]):
                        if cv2.waitKey(1) & 0xFF == 27:
                            cv2.destroyAllWindows()
                            return
                cv2.destroyAllWindows()

    def edit(self):
        self.manager.current = "loadedMedia"

    def settings(self):
        # TODO: develop settings
        self.manager.current = "loadedMedia"

    def quit(self):
        quit()


class LoadedMedia(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # define media directory
        self.MEDIA_LOCATION = r"C:\pythonCode\rollerAds\media"
        # initial states of selected rows for both tables and selected table
        self.selected_row_active = 0
        self.selected_row_inactive = 0
        # load data from JSON file and create active and inactive lists
        self.load_storyboard()
        # define headers
        self.column_data = [
            "#",
            "Name",
            "Filename",
            "Type",
            "Format",
            "Duration",
            "Start Date",
            "End Date",
        ]

    def load_storyboard(self):
        """Load JSON file that holds all media information"""
        # open storyboard JSON data and split into active and not active
        with open(
            os.path.join(
                MAIN.directories[platform.system()], "json", "storyboard.json"
            ),
            mode="r",
        ) as json_file:
            storyboard = json.load(json_file)["loaded_media"]
        MAIN.active_data = sorted(
            [i for i in storyboard if i["active"]], key=lambda i: i["position"]
        )
        MAIN.inactive_data = sorted(
            [i for i in storyboard if not i["active"]], key=lambda i: i["position"]
        )
        self.split_active_and_inactive()

    # Active Table Buttons
    def edit(self):
        row = self.ids.table_active.row_sel_num
        if row == -1:
            return
        idx = self.manager.get_screen("editProperties")
        idx.aka.text = MAIN.active_data[row]["playback"]["aka"]
        idx.file_name.text = MAIN.active_data[row]["playback"]["file_name"]
        idx.type.text = MAIN.active_data[row]["playback"]["type"]
        idx.format.text = MAIN.active_data[row]["playback"]["format"]
        idx.duration.text = str(MAIN.active_data[row]["playback"]["duration"])
        idx.begin.text = MAIN.active_data[row]["playback"]["date_start"]
        idx.end.text = MAIN.active_data[row]["playback"]["date_end"]
        self.manager.current = "editProperties"

    def move_up(self):
        row = self.ids.table_active.row_sel_num
        if row < 0:
            return
        MAIN.active_data[row]["position"], MAIN.active_data[row - 1]["position"] = (
            MAIN.active_data[row - 1]["position"],
            MAIN.active_data[row]["position"],
        )
        self.update_tables()

    def move_down(self):
        row = self.ids.table_active.row_sel_num
        if row >= len(MAIN.active_data) - 1 or row == -1:
            return
        MAIN.active_data[row]["position"], MAIN.active_data[row + 1]["position"] = (
            MAIN.active_data[row + 1]["position"],
            MAIN.active_data[row]["position"],
        )
        self.update_tables()

    def deactivate(self):
        row = self.ids.table_active.row_sel_num
        if len(MAIN.active_data) == 0 or row == -1:
            return
        MAIN.active_data[row]["active"] = False
        MAIN.active_data[row]["position"] = 9999
        self.update_tables()

    # Inactive Table Buttons
    def activate(self):
        row = self.ids.table_inactive.row_sel_num
        if len(MAIN.inactive_data) == 0 or row == -1:
            return
        MAIN.inactive_data[row]["active"] = True
        MAIN.inactive_data[row]["position"] = 999
        self.update_tables()

    def unload(self):
        row = self.ids.table_inactive.row_sel_num
        if len(MAIN.inactive_data) == 0 or row == -1:
            return
        MAIN.inactive_data.pop(row)
        self.update_tables()

    # Right Menu Buttons
    def save(self):
        with open(
            os.path.join(
                MAIN.directories[platform.system()], "json", "storyboard.json"
            ),
            mode="w+",
        ) as json_file:
            json_file.write(
                json.dumps({"loaded_media": MAIN.active_data + MAIN.inactive_data})
            )
        # TODO: remove thumbnail file
        # copy file to media folder
        shutil.copy(
            MAIN.filename,
            os.path.join(MAIN.MEDIA_LOCATION, MAIN.filename.split("\\")[-1]),
        )

    def reset(self):
        self.load_storyboard()
        self.update_tables()

    def update_tables(self):
        self.split_active_and_inactive()
        self.ids.table_active.update_row_data(row_data=self.active_data_formatted)
        self.ids.table_inactive.update_row_data(row_data=self.inactive_data_formatted)
        # reset row number and highlight
        self.ids.table_active.row_sel_num = -1
        self.ids.table_inactive.row_sel_num = -1

    def split_active_and_inactive(self):
        # combine all active and inactive and re-split
        combined = MAIN.active_data + MAIN.inactive_data
        # select all active, sort them ascending and number consecutive from 1
        MAIN.active_data = sorted(
            [i for i in combined if i["active"]], key=lambda i: i["position"]
        )
        for k, i in enumerate(MAIN.active_data, start=1):
            i["position"] = k
        # select all inactive, sort them ascending and number consecutive from 1
        MAIN.inactive_data = sorted(
            [i for i in combined if not i["active"]], key=lambda i: i["position"]
        )
        for k, i in enumerate(MAIN.inactive_data, start=1):
            i["position"] = k
        # create list of images for use with thumbnails
        self.active_thumbnails = [i["thumbnail"] for i in MAIN.active_data]
        self.inactive_thumbnails = [i["thumbnail"] for i in MAIN.inactive_data]
        # flatten information into plain list and add markup formatting
        self.active_data_formatted = flatten_and_format(MAIN.active_data, 14)
        self.inactive_data_formatted = flatten_and_format(MAIN.inactive_data, 14)


class EditProperties(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type_values = list(MAIN.format_options.keys())
        self.format_values = ""

    def edit_save(self):
        # validate data entered before saving
        error_message = ""
        if len(self.ids.aka.text) < 1:
            error_message += "- Name cannot be empty.\n"
        if not self.ids.format.text:
            error_message += "- Format not selected.\n"
        if float(self.ids.duration.text) < 0.1:
            error_message += "- Duration must be greater of equal than 0.1.\n"
        if dt.strptime(self.ids.end.text, "%a, %d %b %Y") < dt.now():
            error_message += "- End date must be in the future."
        if error_message:
            alert = AlertPopup()
            alert.ids.error_message.text = error_message
            alert.open()
            return

        # build new item data structure for "playback" section
        playback_data = {
            "aka": self.ids.aka.text,
            "file_name": self.ids.file_name.text,
            "type": self.ids.type.text,
            "format": self.ids.format.text,
            "duration": f"{float(self.ids.duration.text):.1f}",
            "date_start": self.ids.begin.text,
            "date_end": self.ids.end.text,
            "datetime_start_str": self.ids.begin.text,
            "datetime_end_str": self.ids.end.text,
        }

        # new file: add entire data record + thumbnail
        if MAIN.edit_add_new_file:
            new_item = {
                "id": uuid.uuid4().hex,
                "active": False,
                "position": 9999,
                "thumbnail": f"{uuid.uuid4().hex[:4]}.png",
                "playback": playback_data,
            }
            MAIN.inactive_data.append(new_item)
            # create thumbnail
            self.create_thumbnail(new_item)

        # existing file> replace "playback" section of record
        else:
            row = MAIN.loadedMediaScreenIds.table_active.row_sel_num
            MAIN.active_data[row]["playback"] = playback_data

        MAIN.SCREEN.get_screen("loadedMedia").update_tables()
        self.manager.current = "loadedMedia"
        MAIN.edit_add_new_file = False

    def create_thumbnail(self, new_item):
        thumbnail_file_name = new_item["thumbnail"]
        file_type = new_item["playback"]["type"]
        file_name = new_item["playback"]["file_name"]

        if file_type == "Image":
            img = cv2.imread(os.path.join(MAIN.MEDIA_LOCATION, file_name))
            img = cv2.resize(img, (256, 256))
        elif file_type == "Video":
            video = cv2.VideoCapture(self.filename)
            k = 0
            res = True
            while res and k < 50:
                res, frame = video.read()
                k += 1
            img = cv2.resize(frame, (256, 256))
        cv2.imwrite(
            os.path.join(MAIN.MEDIA_LOCATION, "thumbnails", thumbnail_file_name), img
        )

    def date_picker(self):
        today = dt.now()
        dialog = MDDatePicker(
            mode="range", year=today.year, month=today.month, day=today.day
        )
        dialog.bind(on_save=self.on_date_picker_ok)
        dialog.open()

    def on_date_picker_ok(self, _, value, date_range):
        self.ids.begin.text = dt.strftime(date_range[0], "%a, %d %b %Y")
        self.ids.end.text = dt.strftime(date_range[-1], "%a, %d %b %Y")

    def on_selected_type(self):
        self.ids.format.text = ""
        self.ids.format.values = MAIN.format_options[self.ids.type.text]


class AddNewFile(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drives = [
            i for i in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{i}:")
        ]

    def on_selection(self, _, filename):
        if not filename:
            return

        self.filename = MAIN.filename = filename[0]
        bs = "\\"
        path = bs.join(self.filename.split(bs)[:-1])
        self.ids.selected_file_name.text = (
            f"[b]File Name:[/b] {self.filename.split(bs)[-1]}"
        )
        self.ids.selected_file_path.text = f"[b]File Path:[/b] {path}"
        self.ids.selected_file_size.text = (
            f"[b]File Size:[/b] {os.path.getsize(self.filename)//1024:,} Kb"
        )
        self.ids.selected_file_created.text = f"[b]Created on:[/b] {dt.fromtimestamp(os.path.getctime(self.filename)).strftime('%a, %d %b %Y')}"
        self.ids.selected_file_image.source = self.filename

    def add_file(self):
        # determine type/format
        estimated_format = filetype.guess(self.filename).extension
        type = format = ""
        if estimated_format:
            for types in MAIN.format_options:
                for formats in MAIN.format_options[types]:
                    if estimated_format in formats:
                        format = formats
                        type = types

        idx = self.manager.get_screen("editProperties")
        idx.aka.text = "aka"
        idx.file_name.text = self.filename.split("\\")[-1]
        idx.type.text = type
        idx.format.text = format
        idx.duration.text = "5"
        idx.begin.text = dt.strftime(dt.now(), "%a, %d %b %Y")
        idx.end.text = dt.strftime(dt.now() + timedelta(days=7), "%a, %d %b %Y")
        self.manager.current = "editProperties"

        MAIN.edit_add_new_file = True

    def cancel(self):
        self.manager.current = "loadedMedia"


class AlertPopup(Popup):
    pass


class WindowManager(ScreenManager):
    pass


class KivyApp(MDApp):
    MEDIA_LOCATION = r"C:\pythonCode\rollerAds\media"
    directories = {
        "Windows": r"C:\pythonCode\rollerAds\static",
        "Linux": r"/home/pi/pythonCode/rollerAds\static",
    }
    selected_rows = [-1, -1]
    edit_add_new_file = False
    with open(
        r"C:\pythonCode\rollerAds\controller\mediaTypes.json", mode="r"
    ) as json_file:
        format_options = json.load(json_file)

    def build(self):
        # self.row_selected = 0
        self.SCREEN = Builder.load_file("test.kv")
        self.loadedMediaScreenIds = self.SCREEN.get_screen("loadedMedia").ids
        self.editPropertiesScreenIds = self.SCREEN.get_screen("editProperties").ids
        self.addNewFileScreenIds = self.SCREEN.get_screen("addNewFile").ids
        return self.SCREEN


def flatten_and_format(data, size):
    sz = f"[size={str(size)}]"
    return [
        (
            f'{sz}{str(i["position"])}',
            f'{sz}{i["playback"]["aka"]}',
            f'{sz}{i["playback"]["file_name"]}',
            f'{sz}{i["playback"]["type"]}',
            f'{sz}{i["playback"]["format"]}',
            f'{sz}{str(i["playback"]["duration"])}',
            f'{sz}{i["playback"]["date_start"]}',
            f'{sz}{i["playback"]["date_end"]}',
        )
        for i in data
    ]


# Basic Kivy parameters
Window.size = (1300, 700)
Window.top, Window.left = 50, 50
Window.clearcolor = (0.5, 0.3, 0.2, 1)
MAIN = KivyApp()
MAIN.run()
