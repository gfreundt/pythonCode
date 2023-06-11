from PIL import Image
import numpy as np


def all_color(img, c):
    result = []
    for x in range(74):
        for y in range(74):
            if np.array_equal(img[y][x], c):
                result.append((x, y))
                if x == 26 and y == 72:
                    print("*****")
    return result


total = []
for n in range(1, 7):
    file = Image.open(f"appwhite{n}.png")
    black = [0, 0, 0]
    white = [255, 255, 255]
    appblack = [79, 73, 73]
    appwhite = [222, 221, 222]
    total.append(all_color(np.asarray(file), np.array(appwhite)))

for n in range(1, 7):
    file = Image.open(f"appblack{n}.png")
    total.append(all_color(np.asarray(file), np.array(appblack)))

for item in total[0]:
    if all([item in i for i in total[1:]]):
        print(item)
