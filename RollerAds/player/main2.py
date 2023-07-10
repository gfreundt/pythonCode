import kivy
import os

kivy.require("1.10.0")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp


def tree_printer(root):
    sx, dx = [], []
    for root, dirs, files in os.walk(root):
        for d in dirs:
            dx.append(os.path.join(root, d))
        for f in files:
            sx.append(os.path.join(root, f))
    return sx, dx


class Box2(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        var1, var2 = tree_printer(".")
        print(var1)
        for i in var2:
            b = Button(text=i, size=(dp(20), dp(20)))
            self.add_widget(b)


class MainWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        var1, var2 = tree_printer(".")
        for i in var1:
            b = Label(text=i)
            self.add_widget(b)


class mainkivyApp(App):
    def build(self):
        return Box2()


mainkivyApp().run()
