import pyautogui
from PIL import ImageGrab
from time import time


def need_to_jump():

    px = ImageGrab.grab(bbox=(1650 - x_hit, 450, 1700 - x_hit, 480)).load()

    # img = ImageGrab.grab(bbox=(1650, 450, 1700, 480))
    # px = img.load()
    # for i in range(y_length):
    #     img.putpixel((x_hit, y_hit + i), (255, 0, 0))
    # img.show()
    # quit()

    """
    if [True for i in range(y_hit, y_hit + y_length) if px[x_hit, i] != empty]:
        return True
    elif [True for i in range(y_hit, y_hit + y_length) if px[x_hit + 3, i] != empty]:
        return True
    elif [True for i in range(y_hit, y_hit + y_length) if px[x_hit - 3, i] != empty]:
        return True
    """

    if [
        True
        for i in range(y_hit, y_hit + y_length)
        for j in range(-4, 5)
        if px[j, i] != empty
    ]:
        return True


x_hit = 36
y_hit = 2
y_length = 7
empty = (255, 255, 255)
k = 0

while True:
    if need_to_jump():
        pyautogui.press(" ")
        k += 1
        if k == 7:
            k = 0
            x_hit += 2
