import os, time, io
import numpy as np
from PIL import Image
from statistics import mean

import easyocr

_img1 = "sunarp.png"
_img2 = "sunarp2.png"

img = Image.open(_img1)
img1 = np.asarray(img)

WHITE = np.asarray((255, 255, 255, 255))
BLACK = np.asarray((0, 0, 0, 0))

img = np.asarray(
    [[WHITE if mean(i) > 160 else BLACK for i in j] for j in img1], dtype=np.uint8
)
img = Image.fromarray(img)
img.show()

img.save(_img2)  # , mode="RGBA")

READER = easyocr.Reader(["es"], gpu=False)
c = READER.readtext(_img2, text_threshold=0.7)

for i in c:
    print(i[-2])
