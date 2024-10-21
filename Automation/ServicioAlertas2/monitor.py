from tkinter import Tk, Label
import tkinter.font as TkFont
import streamlit as st
import os


class Monitor:

    def __init__(self) -> None:
        self.counter = 1
        self.table = False

    def add_item(self, text, type=0):
        if type == 0:
            st.subheader(text)
            self.table = False
        elif type == 1:
            st.write(text)
            self.table = False
        elif type == 2:
            if not self.table:
                self.col1, self.col2 = st.columns(2)
                self.table = True
            self.col1.write(text)
        elif type == 3:
            if not self.table:
                self.col1, self.col2 = st.columns(2)
                self.table = True
            self.col2.write(text)
        elif type == 4:
            st.dataframe(data=text, hide_index=True, height=None)
        else:
            st.write(text)

    def add_widget2(self, txt, type=0):
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
        if type == 0:
            st.write(f"<b>{txt}</b>")
        else:
            st.write(f"<i>{txt}</i>")

    def start_monitor(self):
        st.set_page_config(page_title="Monitor", layout="wide")
        st.image(os.path.join(os.curdir, "other", "titleimg.png"))
        st.title("Sistema de Alertas Perú")

    def start_monitor2(self):

        self.current_row = 0

        # init window
        self.window = Tk()
        self.window.title("Sistema de Alertas Peru")
        self.window.geometry("800x1600")
        self.window.config(background="black")

        self.window.mainloop()

    def end_monitor2(self):
        self.window.quit()
