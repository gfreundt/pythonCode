from tkinter import Tk, Label
import tkinter.font as TkFont


class Monitor:

    def __init__(self) -> None:
        self.counter = 1

    def add_widget(self, txt, type=0):
        # level-1 text
        if type == 0:
            self.text = f"{self.counter}. {txt}"
            self.font_size = 12
            self.counter += 1
        # level-2 text
        if type == 1:
            self.text = f"{' ' * 4}> {txt}"
            self.font_size = 10
        # adds to last entry on same line
        if type == 2:
            self.text += f" {txt}"
            self.current_row -= 1
        # level-3 text
        if type == 3:
            self.text = f"{' ' * 8}>> {txt}"

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
