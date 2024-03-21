import pyautogui
import time

pyautogui.FAILSAFE = False

time.sleep(3)

g = []

for m in range(1000):
    time.sleep(0.005)
    g.append(pyautogui.position())

print("done")

time.sleep(5)

for n in g:
    # print(n)
    pyautogui.moveTo(n)
