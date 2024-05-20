import time, io
from gft_utils import ChromeUtils
from selenium.webdriver.common.by import By
from PIL import Image
import pygame
from pygame.locals import *
from gft_utils import pygameUtils

pygame.init()


def captcha_gui(placa, canvas):

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
                    return "".join(chars)

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
