import json
import os
import platform
from datetime import datetime as dt
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.list import OneLineListItem

from kivy.uix.popup import Popup
import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.uix.label import MDLabel
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.clock import Clock


class EditProperties(Screen):
    pass
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.record = {"playback": "test"}
        # data = self.record
        # self.full_record = data
        # self.record = data["playback"]
        # self.ids.aka.text = self.record["aka"]
        # self.ids.file_name.text = self.record["file_name"]
        # self.ids.type.text = self.record["type"]
        # self.ids.format.text = self.record["format"]
        # self.ids.duration.text = str(self.record["duration"])
        # self.ids.begin.text = self.record["datetime_start_str"]
        # self.ids.end.text = self.record["datetime_end_str"]
        # self.open()
        self.response = None

    def cancel(self):
        pass
        # self.dismiss()

    def save(self):
        # update "playback" key with new information from popup
        self.response = self.full_record | (
            {
                "playback": {
                    "aka": self.ids.aka.text,
                    "file_name": self.ids.file_name.text,
                    "type": self.ids.type.text,
                    "format": self.ids.format.text,
                    "duration": self.ids.duration.text,
                    "datetime_start_num": dt.strptime(
                        self.ids.begin.text, "%H:%M:%S %d/%m/%Y"
                    ),
                    "datetime_end_num": dt.strptime(
                        self.ids.end.text, "%H:%M:%S %d/%m/%Y"
                    ),
                    "datetime_start_str": self.ids.begin.text,
                    "datetime_end_str": self.ids.end.text,
                }
            }
        )
        # self.dismiss()
        """


class AddNewFile(Screen):
    pass
    """
    def __init__(self, files, **kwargs):
        super().__init__(**kwargs)

        for file in files:
            self.ids.new_file_list.add_widget(
                OneLineListItem(
                    text=file,
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    divider="Full",
                    divider_color=(0, 0, 1, 1),
                    on_press=self.file_selected,
                    radius=[15, 15, 15, 15],
                    size_hint=(1, 0.5),
                )
            )
        # self.open()

    def add(self):
        preloaded_data = {
            "playback": {
                "aka": "",
                "file_name": self.active_file,
                "type": "",
                "format": "",
                "duration": 0,
                "datetime_start_num": 1666482750,
                "datetime_end_num": 1666482920,
                "datetime_start_str": "03:45:12 12/09/2021",
                "datetime_end_str": "09:55:18 14/09/2021",
            }
        }
        self.table_updater = Clock.schedule_interval(self.auto_updater_new, 0.5)
        self.popup = EditPropertiesPopup(preloaded_data)

    def cancel(self):
        pass
        # self.dismiss()

    def file_selected(self, object):
        # TODO: change path variable and make image variable
        path = r"C:\pythonCode\rollerAds\media"
        self.active_file = object.text
        self.ids.selected_file_image.source = os.path.join(path, object.text)
        self.ids.selected_file_name.text = f"[b]Selected File:[/b] {object.text}"
        s = os.stat(os.path.join(path, object.text)).st_size // 1000
        self.ids.selected_file_created.text = f"[b]File Size:[/b] {s:,} Kb"
        d = dt.fromtimestamp(
            os.stat(os.path.join(path, object.text)).st_ctime
        ).strftime("%m/%d/%Y, %H:%M:%S")
        self.ids.selected_file_size.text = f"[b]Created on:[/b] {d}"

    def auto_updater_new(self, _):
        if self.popup.response:
            print(self.popup.response)
            return

            self.inactive.append(self.popup.response)
            self.update_tables()
            self.table_updater.cancel()
        """


class MainLayout(Screen):
    pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # define media directory
        self.MEDIA_LOCATION = r"C:\pythonCode\rollerAds\media"

        # initial states of selected rows for both tables and selected table
        self.selected_row_active = 0
        self.selected_row_inactive = 0
        self.selected_table = 0

        # load data from JSON file and create active and inactive lists
        self.load_storyboard()
        self.split_active_and_inactive()

        # load generated data into table and replace layout placeholder
        # self.table_active = self.generate_table(
        #     SCREEN.get_screen("main_layout").ids.table_active, self.active_formatted
        # )
        # self.table_inactive = self.generate_table(
        #     self.ids.table_inactive, self.inactive_formatted
        # )

    def row_selected(self, _, cell):
        row = cell.index // 8
        if cell.table.uid == 644:
            thumbnails = self.active_thumbnails
            self.selected_row_active = row
            self.selected_table = 0
        else:
            thumbnails = self.inactive_thumbnails
            self.selected_row_inactive = row
            self.selected_table = 1

        self.ids.image_preview.source = os.path.join(
            self.MEDIA_LOCATION,
            "thumbnails",
            thumbnails[row],
        )

    def move_up(self):
        row = self.selected_row_active
        if row > 0:
            self.active[row]["position"], self.active[row - 1]["position"] = (
                self.active[row - 1]["position"],
                self.active[row]["position"],
            )
            self.update_tables()

    def move_down(self):
        row = self.selected_row_active
        if row < len(self.active_formatted):
            self.active[row]["position"], self.active[row + 1]["position"] = (
                self.active[row + 1]["position"],
                self.active[row]["position"],
            )
            self.update_tables()

    def deactivate(self):
        row = self.selected_row_active
        self.active[row]["active"] = False
        self.active[row]["position"] = 999
        self.update_tables()

    def activate(self):
        row = self.selected_row_inactive
        self.inactive[row]["active"] = True
        self.inactive[row]["position"] = 999
        self.update_tables()

    def unload(self):
        row = self.selected_row_active
        self.inactive.pop(row)
        self.update_tables()

    def save(self):
        print("||||||||||||", self.a.edit_response)

    def load_new_file(self):
        efiles = [i["playback"]["file_name"] for i in self.active + self.inactive]
        files = [
            i for i in os.listdir(self.MEDIA_LOCATION) if i not in efiles and "." in i
        ]
        self.table_updater = Clock.schedule_interval(self.auto_updater_new, 0.5)
        self.add_file = AddNewFilePopup(files)
        print("+++++++++++++", self.add_file)

    def edit_active(self):
        # permanent loop that updates tables if editting generated changes
        self.table_updater = Clock.schedule_interval(self.auto_updater, 0.5)
        self.popup = EditPropertiesPopup(self.active[self.selected_row_active])

    def edit_inactive(self):
        # permanent loop that updates tables if editting generated changes
        self.table_updater = Clock.schedule_interval(self.auto_updater, 0.5)
        self.popup = EditPropertiesPopup(self.inactive[self.selected_row_inactive])

    def update_tables(self):
        self.split_active_and_inactive(reload=True)
        self.table_active.update_row_data(self, self.active_formatted)
        self.table_inactive.update_row_data(self, self.inactive_formatted)

    def auto_updater(self, _):
        if self.popup.response:
            if self.selected_table == 0:
                for k, d in enumerate(self.active):
                    if d["id"] == self.popup.response["id"]:
                        self.active[k] = self.popup.response
            else:
                for k, d in enumerate(self.inactive):
                    if d["id"] == self.popup.response["id"]:
                        self.inactive[k] = self.popup.response

            self.table_updater.cancel()
            self.update_tables()

    def auto_updater_new(self, _):
        if self.add_file.popup.response:
            print("gotcha")
            self.add_file.table_updater.cancel()
            self.update_tables()

    def load_storyboard(self):
        """Load JSON file that holds all media information"""

        # get absolute path depending on OS
        directories = {
            "Windows": r"C:\pythonCode\rollerAds\static",
            "Linux": r"/home/pi/pythonCode/rollerAds\static",
        }
        # open storyboard JSON data and split into active and not active
        with open(
            os.path.join(directories[platform.system()], "json", "storyboard.json"),
            mode="r",
        ) as json_file:
            storyboard = json.load(json_file)["loaded_media"]
        self.active = sorted(
            [i for i in storyboard if i["active"]], key=lambda i: i["position"]
        )
        self.inactive = sorted(
            [i for i in storyboard if not i["active"]], key=lambda i: i["position"]
        )

    def split_active_and_inactive(self, reload=False):
        if reload:
            ai = self.active + self.inactive
            # select all active, sort them ascending and number consecutive from 1
            self.active = sorted(
                [i for i in ai if i["active"]], key=lambda i: i["position"]
            )
            for k, i in enumerate(self.active, start=1):
                i["position"] = k
            # select all inactive, sort them ascending and number consecutive from 1
            self.inactive = sorted(
                [i for i in ai if not i["active"]], key=lambda i: i["position"]
            )
            for k, i in enumerate(self.inactive, start=1):
                i["position"] = k

        # create list of images for use with thumbnails
        self.active_thumbnails = [i["thumbnail"] for i in self.active]
        self.inactive_thumbnails = [i["thumbnail"] for i in self.inactive]

        # flatten information into plain list and add markup formatting
        self.active_formatted = flatten_and_format(self.active, 14)
        self.inactive_formatted = flatten_and_format(self.inactive, 14)

    def generate_table(self, table_id, table_data):
        new_table = MDDataTable(
            column_data=[
                ("#", dp(15)),
                ("Name", dp(30)),
                ("Filename", dp(35)),
                ("Type", dp(15)),
                ("Format", dp(15)),
                ("Duration", dp(25)),
                ("Start Date", dp(30)),
                ("End Date", dp(30)),
            ],
            background_color="#FF0000",
            background_color_header="#b0bec5",
            # background_color_cell="#ebf4f1",
            background_color_selected_cell="#e6b400",
            elevation=2,
            use_pagination=True,
        )
        new_table.row_data = table_data
        new_table.bind(on_row_press=self.row_selected)
        table_id.add_widget(new_table)
        return new_table


class WindowManager(ScreenManager):
    pass


class KivyCode(MDApp):
    def build(self):
        # self.theme_cls.theme_style = "Dark"
        # self.theme_cls.primary_palette = "DeepPurple"
        # self.theme_cls.accent_palette = "Red"
        print("1", SC)
        return SC


def flatten_and_format(data, size):
    # ("alert", color1, r["playback"]["file_name"]),
    sz = f"[size={str(size)}]"
    return [
        (
            f'{sz}{str(i["position"])}',
            f'{sz}{i["playback"]["aka"]}',
            f'{sz}{i["playback"]["file_name"]}',
            f'{sz}{i["playback"]["type"]}',
            f'{sz}{i["playback"]["format"]}',
            f'{sz}{str(i["playback"]["duration"])} s',
            f'{sz}{i["playback"]["datetime_start_str"]}',
            f'{sz}{i["playback"]["datetime_end_str"]}',
        )
        for i in data
    ]


# Basic Kivy parameters
kivy.require("2.1.0")
Window.size = (1500, 900)
Window.top, Window.left = 50, 50
Window.clearcolor = (0.5, 0.3, 0.2, 1)
SC = Builder.load_file("controller.kv")

# Run Kivy framework
KivyCode().run()
