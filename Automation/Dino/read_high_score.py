import easyocr
from PIL import Image
import os


reader = easyocr.Reader(
    ["en"]
)  # this needs to run only once to load the model into memory
for file in os.listdir():
    if "png" in file:
        print(reader.readtext(image=file))
