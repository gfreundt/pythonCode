import os
import logging
import threading
import time
from tkinter import Tk, Label, LEFT, TOP, Frame, BOTTOM
from PIL import ImageTk, Image


class Monitor:

    def __init__(self) -> None:

        # self.logger = self.start_logger()

        self.console_dims = (2000, 1450)
        self.console_rows = 35
        self.console_cols = 4
        self.console_text = []
        self.console_styles = [24, 20, 14, 12, 10]

        self.console_col_width = self.console_dims[0] // self.console_cols
        self.active_col = 0
        self.previous_col = int(self.console_cols)
        self.active_row = 0

        # open console in independent thread
        t1 = threading.Thread(target=self.start_console, daemon=True)
        t1.start()
        # give window enough time to open before receiving text
        time.sleep(0.5)

    def log(self, txt, type="0R", error=False):
        # type structure: first digit = font size *descending), second = Regular/Bold
        type = str(type)
        font_size = self.console_styles[int(type[0])]
        font_name = f"Arial{' Bold' if 'B' in type else ''}"
        self.console_add_text(txt, font=(font_name, font_size))

    def start_logger(self):
        """Start logger, always use same log file."""
        # TODO: include parameters to split file into smaller versions
        LOG_PATH = os.path.join("..", "logs", "alerts_log.txt")
        logging.basicConfig(
            filename=LOG_PATH,
            filemode="a",
            format="%(asctime)s | %(levelname)s | %(message)s",
        )
        _log = logging.getLogger(__name__)
        _log.setLevel(logging.INFO)
        return _log

    def start_console(self):
        self.window = Tk()
        self.window.geometry(f"{self.console_dims[0]}x{self.console_dims[1]}")
        self.window.config(background="black")
        self.window.mainloop()

    def console_add_text(self, txt, font):
        print("---->", txt)
        self.console_text.append((txt, font))
        self.console_display_text((txt, font))

    def console_display_text(self, text):

        def erase_column(col):
            return
            for y in range(0, self.console_rows):
                Label(master=self.window, text=" " * 40, bg="black").grid(
                    column=col, row=y
                )

        # write new text information into next place
        Label(
            master=self.window,
            text=text[0],
            font=text[1],
            fg="white",
            bg="black",
            justify="left",
        ).pack(anchor="w")
        # grid(row=self.active_row * 10, column=self.active_col * 40)

        # define place for next text -- if end of row got to next col, if last col, start from left
        self.active_row += 1
        if self.active_row == self.console_rows:
            self.active_row = 0
            self.active_col += 1
            if self.active_col == self.console_cols:
                self.active_col = 0
            # erase data in column
            erase_column(self.active_col)

    def change_label(self, txt):
        self.label = Label(master=self.window, text=txt)
        self.label.grid(row=0, column=0)

    def test(self, txt):
        self.label = Label(master=self.window, text=txt)
        self.label.grid(row=0, column=0)
