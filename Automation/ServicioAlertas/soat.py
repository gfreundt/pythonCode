import time, io
from gft_utils import ChromeUtils
from selenium.webdriver.common.by import By
from PIL import Image
import pygame
from pygame.locals import *
from gft_utils import pygameUtils
import subprocess
import random

pygame.init()


def captcha_gui(SOAT, placa, canvas):

    def disp_capture(chars, message):
        if message:
            canvas.MAIN_SURFACE.fill(canvas.COLORS["BLACK"])
            text = canvas.FONTS["NUN80B"].render(
                message,
                True,
                canvas.COLORS["RED"],
                canvas.COLORS["BLACK"],
            )
            canvas.MAIN_SURFACE.blit(
                text,
                (
                    UPPER_LEFT[0] + 465 + 50,
                    UPPER_LEFT[1],
                ),
            )
        else:
            chars = f"{''.join(chars):<6}"
            for col in range(6):
                text = canvas.FONTS["NUN80B"].render(
                    chars[col],
                    True,
                    canvas.COLORS["BLACK"],
                    canvas.COLORS["WHITE"],
                )
                TEXTBOX.fill(canvas.COLORS["WHITE"])
                TEXTBOX.blit(text, (12, 5))
                canvas.MAIN_SURFACE.blit(
                    TEXTBOX,
                    (
                        col * 90 + UPPER_LEFT[0] + 20 + 465,
                        UPPER_LEFT[1],
                    ),
                )
        pygame.display.flip()

    TEXTBOX = pygame.Surface((80, 105))
    UPPER_LEFT = (10, 10)
    image = pygame.image.load("captcha_soat.png").convert()
    canvas.MAIN_SURFACE.fill(canvas.COLORS["BLACK"])
    canvas.MAIN_SURFACE.blit(image, UPPER_LEFT)

    chars, col, msg = [], 0, ""
    while True:
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
                    except:
                        pass

                disp_capture(chars, message=msg)

                if col == 6:
                    response = SOAT.browser(placa=placa, captcha_txt="".join(chars))
                    if response == -1:
                        msg = "Limit"
                        SOAT.limit = True

                    elif response == -2:
                        msg = "Captcha"

                    else:
                        msg = "Ok"
                        time.sleep(2)

                    disp_capture(chars, message=msg)
                    time.sleep(2)
                    return response

        disp_capture(chars, message=msg)


def get_captcha_image(SOAT):
    cmd = "C:\Program Files\Private Internet Access\piactl.exe"
    regions = ["chile", "argentina", "peru", "brazil", "mexico", "ecuador"]

    # turn off VPN if limit reached to get captcha image
    if SOAT.limit:
        subprocess.run([cmd, "disconnect"], shell=True)

    SOAT.WEBD.refresh()
    _img = SOAT.WEBD.find_element(
        By.XPATH,
        "/html/body/div/main/article/div/section[2]/div/div/div[1]/div/div[3]/div[1]/form/div[2]/img",
    )
    # turn on VPN if limit reached to skip IP limiting
    if SOAT.limit:
        subprocess.run([cmd, "set", "region", random.choice(regions)], shell=True)
        subprocess.run([cmd, "connect"], shell=True)
    captcha_img = Image.open(io.BytesIO(_img.screenshot_as_png)).resize((465, 105))
    captcha_img.save("captcha_soat.png")


def main(SOAT, placas):

    # don't run if no records to process
    if not placas:
        return []

    # turn off VPN
    cmd = "C:\Program Files\Private Internet Access\piactl.exe"
    subprocess.run([cmd, "disconnect"], shell=True)

    URL = "https://www.apeseg.org.pe/consultas-soat/"
    SOAT.WEBD = ChromeUtils().init_driver(
        headless=True, verbose=False, maximized=True, incognito=True
    )
    SOAT.WEBD.get(URL)
    SOAT.limit = False
    canvas = pygameUtils(screen_size=(1050, 130))

    all_responses = []
    for placa in placas:
        while True:
            try:
                get_captcha_image(SOAT)
                response = captcha_gui(SOAT, placa[4], canvas)
                if type(response) != int:
                    all_responses.append((placa[0], placa[1], response))
                    break
            except KeyboardInterrupt:
                quit()
            except:
                time.sleep(3)
                SOAT.WEBD.refresh()
                break

    # turn off VPN and return responses
    subprocess.run([cmd, "disconnect"], shell=True)
    return all_responses
