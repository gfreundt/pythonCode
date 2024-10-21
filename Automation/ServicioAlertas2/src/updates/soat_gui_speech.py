import io
import threading
from tkinter import Tk, Label
from PIL import Image, ImageTk

from gft_utils import SpeechUtils


def get_captcha(img):
    # show image in separated thread
    t1 = threading.Thread(target=show_captcha, args=(img,), daemon=True)
    t1.start()
    # capture captcha with speech
    return get_speech()


def show_captcha(captcha_img):
    # show captcha image on screen from image object (not filename)

    # define a context to be used in thread for Streamlit to work
    window = Tk()
    window.geometry("1085x245")
    window.config(background="black")
    img = Image.open(io.BytesIO(captcha_img)).resize((1085, 245))
    _img = ImageTk.PhotoImage(master=window, image=img)
    label = Label(master=window, image=_img)
    label.grid(row=0, column=0)
    window.mainloop()


def get_speech():
    # capture speech and return only if it matches criteria
    while True:
        text = SpeechUtils().get_speech()

        # eliminate blank spaces
        text = text.lower().replace(" ", "")

        # show captured text
        print(f"Captured: {text}")

        # if speech is "pass" return wrong captcha to request a new one
        if text.lower() == "pass":
            return "xxxxxx"

        # only accept 6-letter captchas
        if len(text) == 6:
            print("[ACCEPTED]")
            return text
        else:
            print("[NOT VALID]")
