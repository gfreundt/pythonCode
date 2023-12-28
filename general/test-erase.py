import pyautogui
import time
import webbrowser


time.sleep(5)

word = "Procrastination"

for w in word:
    pyautogui.typewrite(w)
    time.sleep(0.2)
