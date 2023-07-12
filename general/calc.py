import kivy

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.lang import Builder


class Calculator(BoxLayout):

    display = "487"

    def digit(self, value):
        if value == "." and "." in self.display:
            return
        if self.display == "0":
            self.display = str(value)
        else:
            self.display += str(value)
        print(self.display)

    def action(self, do):
        match do:
            case "+":
                print("plus")
            case "-":
                print("minus")
            case "*":
                print("mult")
            case "/":
                print("div")


class CalculatorApp(App):
    Window.size = (350, 600)

    def build(self):
        return Calculator()


# Builder.load_file("calculator.kv")
CalculatorApp().run()
