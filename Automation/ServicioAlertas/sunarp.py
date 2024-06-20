import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from statistics import mean
from datetime import datetime as dt
from google.cloud import vision


def process_image(img_object, img_filename):
    WHITE = np.asarray((255, 255, 255, 255))
    BLACK = np.asarray((0, 0, 0, 0))

    _img_object = np.asarray(img_object)
    if np.size(_img_object) == 0:
        return

    # filter out greys for OCR
    img_for_ocr = np.asarray(
        [[WHITE if mean(i) > 165 else BLACK for i in j] for j in _img_object],
        dtype=np.uint8,
    )
    img_for_ocr = Image.fromarray(img_for_ocr)

    # create new larger image, copy original and leave space for frame
    width, height = img_for_ocr.size
    img = Image.new(size=(width + 20, height + 60), mode="RGB", color="white")
    img.paste(img_object, (20, 14))
    img1 = ImageDraw.Draw(img)

    # draw frame with four rectangles
    for coords in (
        [(0, 0), (width + 10, 14)],
        [(0, height + 20), (width + 20, height + 60)],
        [(0, 0), (14, height + 60)],
        [(width + 6, 0), (width + 20, height + 60)],
    ):

        img1.rectangle(
            coords,
            fill="#3A6B8A",
        )

    # add text at bottom (center measuring size previously)
    months = [
        "Ebero",
        "Febrero",
        "Marzp",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Setiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    font = ImageFont.truetype(
        os.path.join("D:", "\pythonCode", "Resources", "Fonts", "montserrat.ttf"), 20
    )
    _text = (
        f"Sistema de Alertas Perú - {months[int(dt.now().month)-1]}, {dt.now().year}"
    )
    size = img1.textlength(_text, font=font)
    img1.text(
        xy=((width + 20 - size) // 2, height + 28), text=_text, fill="white", font=font
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

    # print(content)

    output = []
    # clean text (remove titles)
    content = content.replace(";", ":")
    for symbol in "*./-'+" + '"':
        content = content.replace(symbol, "")

    for line in content.splitlines()[:-1]:
        if ":" in line:
            if len(line.split(":")[1]) > 1:
                output.append(line.split(":")[1].strip())
        else:
            output.append(line.strip())

    # remove fields with one character
    output = [i for i in output if len(i) > 1]

    # if ocr does not return expected structure, return empty
    print(output)
    if len(output) < 14:
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
        _response = [j.strip() for j in output[:12]]
        _response.append(" + ".join(output[12:]))
        _response.append(year_guide[output[2][9]])
        return _response
    except:
        return []
