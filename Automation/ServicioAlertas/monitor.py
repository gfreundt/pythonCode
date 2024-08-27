from tkinter import Tk, Label
import tkinter.font as TkFont


import time


class Monitor:

    def __init__(self) -> None:
        self.counter = 1

    def add_widget(self, txt, type=0):
        if type == 0:
            self.text = f"{self.counter}. {txt}"
            self.font_size = 12
            self.counter += 1
        if type == 1:
            self.text = f"{' ' * 4}> {txt}"
            self.font_size = 10
        if type == 2:
            self.text += f" {txt}"
            self.current_row -= 1
        if type == 3:
            self.text = f"{' ' * 8}>> {txt}"
            self.current_row -= 1

        label = Label(
            self.window,
            font=TkFont.Font(family="Cascadia Mono", size=self.font_size),
            text=f"{self.text:<40}",
            justify="left",
            fg="white",
            bg="black",
        )
        label.grid(row=self.current_row, column=1)
        self.current_row += 1

    def start_monitor(self):
        # init window
        self.window = Tk()

        # define variables
        # self.font = TkFont.Font(family="Cascadia Mono", size=16)
        self.current_row = 0

        # window characteristics
        self.window.title("Sistema de Alertas Peru")
        self.window.geometry("800x1600")
        self.window.config(background="black")

        # endless loop
        self.window.mainloop()

    def end_monitor(self):
        self.window.quit()

    def test(self):
        fonts = list(TkFont.families())
        for f in fonts:
            _font = TkFont.Font(family=f, size=50)
            label1 = Label(
                self.window,
                font=_font,
                text=f"{f:>30}",
                fg="white",
                bg="black",
            )
            label1.grid(row=1, column=1)
            time.sleep(1)


# Cascadia Mono
# Roboto
# Bahnschrift
