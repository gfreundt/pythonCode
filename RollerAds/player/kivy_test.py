import kivy

kivy.require("1.10.0")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout


class Box(BoxLayout):
    pass


class MainWidget(Widget):
    pass


class MainKivyApp(App):
    pass


MainKivyApp().run()
