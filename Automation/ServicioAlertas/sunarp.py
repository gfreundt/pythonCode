import time, io, os
from selenium.webdriver.common.by import By
import pygame
from pygame.locals import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from statistics import mean
from datetime import datetime as dt
from google.cloud import vision
from pprint import pprint


from gft_utils import ChromeUtils, pygameUtils

pygame.init()


def gui(canvas, captcha_img):
    TEXTBOX = pygame.Surface((80, 120))
    UPPER_LEFT = (10, 10)
    image = pygame.image.load(io.BytesIO(captcha_img)).convert()
    image = pygame.transform.scale(image, (500, 120))
    canvas.MAIN_SURFACE.fill(canvas.COLORS["BLACK"])
    canvas.MAIN_SURFACE.blit(image, UPPER_LEFT)

    chars, col = [], 0
    while True:
        # pygame capture screen update
        charsx = f"{''.join(chars):<6}"
        for colx in range(6):
            text = canvas.FONTS["NUN80B"].render(
                charsx[colx],
                True,
                canvas.COLORS["BLACK"],
                canvas.COLORS["WHITE"],
            )
            TEXTBOX.fill(canvas.COLORS["WHITE"])
            TEXTBOX.blit(text, (12, 5))
            canvas.MAIN_SURFACE.blit(
                TEXTBOX,
                (
                    colx * 90 + UPPER_LEFT[0] + 20 + 500,
                    UPPER_LEFT[1],
                ),
            )
        pygame.display.flip()

        # capture keystrokes and add to manual captcha input
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT or (event.type == KEYDOWN and event.key == 27):
                quit()
            elif event.type == KEYDOWN:
                if event.key == K_BACKSPACE:
                    if col == 0:
                        continue
                    chars = chars[:-1]
                    col -= 1
                elif event.key in (K_SPACE, K_RETURN):
                    continue
                else:
                    try:
                        chars.append(chr(event.key))
                        col += 1
                    except KeyboardInterrupt:
                        pass

        # if all chars are complete, return manual captcha as string
        if col == 6:
            canvas.MAIN_SURFACE.fill(canvas.COLORS["GREEN"])
            pygame.display.flip()
            return "".join(chars)


def get_captcha_image(SUNARP):
    SUNARP.WEBD.refresh()
    _img = SUNARP.WEBD.find_element(
        By.ID,
        "ctl00_MainContent_captcha_Placa",
    )
    return _img.screenshot_as_png


def process_image(img_object, path):
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
    _new_path = os.path.join(os.curdir, "data", "images", os.path.basename(path))
    img.save(_new_path, mode="RGB")


def parse_text_from_image(img_path):

    client = vision.ImageAnnotatorClient()
    with open(os.path.join(os.curdir, "data", "images", img_path), "rb") as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    raw_text = [i.description for i in response.text_annotations]

    print(raw_text)

    z = []
    # split response in individual lines
    for line in raw_text.splitlines():
        # if line has colon, append as two different items
        if ":" in line:
            z.append(line.split(":")[0].strip())
            z.append(line.split(":")[1].strip())
        else:
            z.append(line)

    # eliminate empty items
    y = [i for i in z if i]

    # build structured response
    col = "SERIE" in y[2]
    response = {
        "placa_validacion": y[8] if col else y[2],
        "serie": y[9] if col else y[4],
        "vin": y[10] if col else y[6],
        "motor": y[11] if col else y[8],
        "color": y[12] if col else y[10],
        "marca": y[13] if col else y[12],
        "modelo": y[14],
        "año": (y[10] if col else y[6]),
        "placa_vigente": y[16],
        "placa_anterior": y[18],
        "estado": y[20],
        "anotaciones": y[22],
        "sede": y[24],
        "propietarios": y[26:],
    }

    return response


def main(SUNARP, placas):
    URL1 = "https://www.gob.pe/sunarp"
    URL2 = "https://www.sunarp.gob.pe/consulta-vehicular.html"
    SUNARP.WEBD = ChromeUtils().init_driver(
        headless=True, verbose=False, maximized=True, incognito=True
    )
    SUNARP.WEBD.get(URL1)
    time.sleep(2)
    SUNARP.WEBD.get(URL2)
    time.sleep(1)
    canvas = pygameUtils(screen_size=(1070, 140))

    all_responses = []
    for placa in placas:
        while True:
            try:
                # load captcha from webpage
                captcha_img = get_captcha_image(SUNARP)

                # capture captcha manually
                captcha_txt = gui(canvas, captcha_img)

                # attempt to scrape image
                response = SUNARP.browser(placa=placa[4], captcha_txt=captcha_txt)

                # scrape succesful: process image and save to disk
                if type(response) != int:
                    img_path = f"SUNARP_{placa[4]}.png"
                    process_image(response, img_path)
                    all_responses.append(
                        (
                            placa[0],
                            placa[1],
                            {
                                "archivo": img_path,
                                "informacion": parse_text_from_image(img_path),
                            },
                        )
                    )
                    pprint(all_responses)
                    # save captcha image with text as filename
                    with open(
                        (
                            os.path.join(
                                os.curdir,
                                "images",
                                "captchas_sunarp",
                                f"{captcha_txt}.png",
                            )
                        ),
                        "wb",
                    ) as outfile:
                        outfile.write(captcha_img)
                    break
                # scrape succesful: no image in database, respond blank
                elif response > 0:
                    all_responses.append((placa[0], placa[1], ""))
                    break
                # if scrape unsuccesful (wrong captcha or image did not load) recycle
            except KeyboardInterrupt:
                quit()
            # except:
            #     time.sleep(3)
            #     SUNARP.WEBD.refresh()
            #     break

    return all_responses