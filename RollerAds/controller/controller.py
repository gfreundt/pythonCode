import json, time
import os
import platform
from datetime import datetime as dt
from datetime import timedelta as td
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRoundFlatButton
from kivymd.uix.behaviors import HoverBehavior
import kivy
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.image import Image


class Layout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # set orientation of main boxlayout
        self.orientation = "vertical"

        # load active and inactive data and create two lists (active amd inactive)
        self.load_storyboard()
        self.split_active_and_inactive()

        # relative size of tables according to rows in each
        # sh_top = len(self.active_formatted) / (
        #     len(self.active_formatted) + len(self.inactive_formatted)
        # )
        # sh_bottom = 1 - sh_top

        # initial states of selected rows for both tables
        self.selected_row_active = 0
        self.selected_row_inactive = 0

        # split main box layout into two parts (Widget A, Widget B)
        top_block = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=(10, 0, 10, 10),
            size_hint=(1, 0.5),
        )
        bottom_block = BoxLayout(
            orientation="vertical",
            spacing=15,
            padding=(10, 20, 10, 10),
            size_hint=(1, 0.5),
        )

        # populate Widget A box with title, table and button section
        new_title = MDLabel(
            markup=True, text="[b]Active[/b]", size_hint=(0.75, 0.1), halign="center"
        )
        new_title.font_size = 30
        new_midsection = BoxLayout(
            orientation="horizontal",
            spacing=5,
            padding=(5, 5, 5, 5),
            size_hint=(1, 0.8),
        )
        new_widget = BoxLayout(
            orientation="horizontal",
            spacing=5,
            padding=(5, 5, 5, 5),
            size_hint=(1, 0.1),
        )

        # insert table and preview zone in midsection
        self.image_preview = Image(
            source=os.path.join(
                MEDIA_LOCATION, "thumbnails", self.active_thumbnails[0]
            ),
        )
        self.image_preview.size_hint = (0.25, 1)
        self.table1 = self.generate_table(self.active_formatted)
        new_midsection.add_widget(self.table1)
        new_midsection.add_widget(self.image_preview)

        # insert buttons into button section
        new_widget.add_widget(MDRoundFlatButton(text="Move Up", on_press=self.move_up))
        new_widget.add_widget(
            MDRoundFlatButton(text="Move Down", on_press=self.move_down)
        )
        new_widget.add_widget(
            MDRoundFlatButton(text="DeActivate", on_press=self.deactivate)
        )

        # combine all three pieces of Widget A
        top_block.add_widget(new_title)
        top_block.add_widget(new_midsection)
        top_block.add_widget(new_widget)

        # populate Widget B box with title, table and button section
        new_title = MDLabel(
            markup=True, text="[b]InActive[/b]", size_hint=(0.75, 0.1), halign="center"
        )
        new_title.font_size = 30
        new_midsection = BoxLayout(
            orientation="horizontal",
            spacing=5,
            padding=(5, 5, 5, 5),
            size_hint=(1, 0.8),
        )
        new_widget = BoxLayout(
            orientation="horizontal",
            spacing=5,
            padding=(5, 5, 5, 5),
            size_hint=(1, 0.1),
        )
        time.sleep(5)

        # insert table and final buttons
        final_buttons = BoxLayout(
            orientation="vertical", spacing=5, padding=(5, 5, 5, 5), size_hint=(0.25, 1)
        )
        final_buttons.add_widget(MDRoundFlatButton(text="Save", on_press=self.save))
        final_buttons.add_widget(MDRoundFlatButton(text="Reset", on_press=self.reset))
        final_buttons.add_widget(
            MDRoundFlatButton(text="Load New File", on_press=self.load)
        )

        self.table2 = self.generate_table(self.inactive_formatted)
        new_midsection.add_widget(self.table2)
        new_midsection.add_widget(final_buttons)

        # insert buttons into button section
        new_widget.add_widget(
            MDRoundFlatButton(text="Activate", on_press=self.activate)
        )
        new_widget.add_widget(MDRoundFlatButton(text="UnLoad", on_press=self.unload))

        # combine all three pieces of Widget B
        bottom_block.add_widget(new_title)
        bottom_block.add_widget(new_midsection)
        bottom_block.add_widget(new_widget)

        # combine Widget A and Widget B
        self.add_widget(top_block)
        self.add_widget(bottom_block)

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
        self.active = [i for i in storyboard if i["active"]]
        self.inactive = [i for i in storyboard if not i["active"]]

    def split_active_and_inactive(self, reload=False):

        if reload:
            ai = self.active + self.inactive
            self.active = [i for i in ai if i["active"]]
            self.inactive = [i for i in ai if not i["active"]]

        # create list of images for use with thumbnails
        self.active_thumbnails = [i["thumbnail"] for i in self.active]
        self.inactive_thumbnails = [i["thumbnail"] for i in self.inactive]

        # flatten information into plain list and add markup formatting
        self.active_formatted = flatten_and_format(self.active, 14)
        self.inactive_formatted = flatten_and_format(self.inactive, 14)

    def generate_table(self, table_data):
        new_table = MDDataTable(
            column_data=[
                ("#", dp(15)),
                ("Name", dp(30)),
                ("Filename", dp(35)),
                ("Type", dp(10)),
                ("Format", dp(15)),
                ("Audio", dp(10)),
                ("Duration", dp(20)),
                ("Start Date", dp(30)),
                ("End Date", dp(30)),
            ],
            background_color_header="#b0bec5",
            background_color_cell="#ebf4f1",
            background_color_selected_cell="#e6b400",
            elevation=2,
        )
        new_table.row_data = table_data
        new_table.bind(on_row_press=self.row_selected)
        new_table.size_hint = (0.75, 1)
        return new_table

    def row_selected(self, _, row):
        if row.table.uid == 429:
            self.selected_row_active = row.index // 9
            self.image_preview.source = os.path.join(
                MEDIA_LOCATION,
                "thumbnails",
                self.active_thumbnails[self.selected_row_active],
            )

        else:
            self.selected_row_inactive = row.index // 9
            self.image_preview.source = os.path.join(
                MEDIA_LOCATION,
                "thumbnails",
                self.inactive_thumbnails[self.selected_row_inactive],
            )

    def move_up(self, _):
        row = self.selected_row_active
        if row > 0:
            self.active_formatted[row], self.active_formatted[row - 1] = (
                self.active_formatted[row - 1],
                self.active_formatted[row],
            )
            self.table1.update_row_data(self, self.active_formatted)

    def move_down(self, _):
        row = self.selected_row_active
        if row < len(self.active_formatted):
            self.active_formatted[row], self.active_formatted[row + 1] = (
                self.active_formatted[row + 1],
                self.active_formatted[row],
            )
            self.table1.update_row_data(self, self.active_formatted)

    def deactivate(self, _):
        row = self.selected_row_active
        self.active[row]["active"] = False
        self.split_active_and_inactive()
        self.table1.update_row_data(self, self.active_formatted)
        self.table2.update_row_data(self, self.inactive_formatted)

        for i in self.active_formatted:
            print(i)
        print("********************")
        for i in self.inactive_formatted:
            print(i)

    def activate(self, _):
        row = self.selected_row_inactive
        self.inactive[row]["active"] = True
        self.split_active_and_inactive(reload=True)
        self.table1.update_row_data(self, self.active_formatted)
        self.table2.update_row_data(self, self.inactive_formatted)

    def unload(self, _):
        pass

    def save(self, _):
        pass

    def reset(self, _):
        pass

    def load(self, _):
        pass


class KivyApp(MDApp):
    def build(self):
        #     self.theme_cls.them_style = "Light"
        #     self.theme_cls.primary_palette = "BlueGray"
        return Layout()


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
            f'{sz}{str(i["playback"]["audio"])}',
            f'{sz}{str(i["playback"]["duration"])} s',
            f'{sz}{i["playback"]["datetime_start_str"]}',
            f'{sz}{i["playback"]["datetime_end_str"]}',
        )
        for i in data
    ]


def main():
    global MEDIA_LOCATION
    MEDIA_LOCATION = r"C:\pythonCode\rollerAds\media"
    kivy.require("2.1.0")
    Window.size = (1500, 900)
    Window.top = 50
    Window.left = 50
    Window.clearcolor = (1, 0, 0, 1)
    KivyApp().run()


main()
