import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from statistics import mean
from datetime import datetime as dt
from google.cloud import vision


def process_image(img_object, img_filename):
    WHITE = np.asarray((255, 255, 255, 255))
    BLACK = np.asarray((0, 0, 0, 0))

    # open downloaded image, filter out greys
    original_img = np.asarray(img_object)
    original_img = np.asarray(
        [[WHITE if mean(i) > 165 else BLACK for i in j] for j in original_img],
        dtype=np.uint8,
    )
    original_img = Image.fromarray(original_img)

    # create new blank image
    width, height = original_img.size
    img = Image.new(size=(width + 20, height + 50), mode="RGB", color="white")
    img.paste(original_img, (20, 14))
    img1 = ImageDraw.Draw(img)

    # draw frame with four rectangles
    for coords in (
        [(0, 0), (width + 10, 14)],
        [(0, height + 10), (width + 20, height + 50)],
        [(0, 0), (14, height + 50)],
        [(width + 6, 0), (width + 20, height + 50)],
    ):

        img1.rectangle(
            coords,
            fill="#3A6B8A",
        )

    # add text at bottom (center measuring size previously)
    font = ImageFont.truetype(
        os.path.join("D:", "\pythonCode", "Resources", "Fonts", "montserrat.ttf"), 20
    )
    _text = f"Sunarp ({dt.now().month:02d} / {dt.now().year})"
    size = img1.textlength(_text, font=font)
    img1.text(
        xy=((width + 20 - size) // 2, height + 17), text=_text, fill="white", font=font
    )

    # enlarge image and save
    factor = 2.5
    img = img.resize((int(width * factor), int(height * factor)))
    img.save(os.path.join(os.curdir, "data", "images", img_filename), mode="RGB")


def ocr_and_parse(img_filename):
    # open saved image from scraping
    with open(
        os.path.join(os.curdir, "data", "images", img_filename), "rb"
    ) as image_file:
        content = image_file.read()

    # perform ocr
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    content = [i.description for i in response.text_annotations][0]

    # clean text (remove titles)
    output = []
    for line in content:
        line = line.strip()
        if ":" in line:
            output.append(line.split(":")[1])
        else:
            output.append(line)

    # clean text (remove empty)
    values = [i for i in output if i]

    # if ocr does not return expected structure, return empty
    if len(values) < 14:
        return []

    year_guide = {
        "1": "2031",
        "2": "2032",
        "3": "2033",
        "4": "2034",
        "5": "2035",
        "6": "2036",
        "7": "2037",
        "8": "2038",
        "9": "2039",
        "A": "2010",
        "B": "2011",
        "C": "2012",
        "D": "2013",
        "E": "2014",
        "F": "2015",
        "G": "2016",
        "H": "2017",
        "J": "2018",
        "K": "2019",
        "L": "2020",
        "M": "2021",
        "N": "2022",
        "P": "2023",
        "R": "2024",
        "S": "2025",
        "T": "2026",
        "V": "2027",
        "W": "2028",
        "X": "2029",
        "Y": "2030",
    }

    # build text response from scraping
    try:
        _response = [j.strip() for j in values]
        _response.append(" + ".join(values[12:-1]))
        _response.append(year_guide[values[2][9]])
        return _response
    except:
        return []
