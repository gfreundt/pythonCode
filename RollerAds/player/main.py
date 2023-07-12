import time
from datetime import timedelta as td
from datetime import datetime as dt

import kivy
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

kivy.require("1.10.0")


def human_readable_secs(seconds):
    # timerStr = StringProperty(human_readable_secs(elapsedSec))
    hours = int(seconds // 3600)
    mins = int((seconds - hours * 3600) // 60)
    secs = int(seconds - hours * 3600 - mins * 60)
    dsecs = int((seconds - hours * 3600 - mins * 60 - secs) * 10)
    return f"{hours:02d}:{mins:02d}:{secs:02d}.{dsecs:01d}"


class Clock(BoxLayout):

    count = 0
    strCount = StringProperty("0")

    def add(self):
        self.count += 1
        self.strCount = str(self.count)

    def substract(self):
        if self.count > 0:
            self.count -= 1
            self.strCount = str(self.count)

    def reset(self):
        self.count = 0
        self.strCount = str(self.count)


class MainKivyApp(App):
    def build(self):
        return Clock()


MainKivyApp().run()
