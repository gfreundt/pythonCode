import pygame
import os
import time
import random as rnd

pygame.init()
clock = pygame.time.Clock()


class Main:
    def __init__(self, box_x0, box_y0, x_margin, x_width) -> None:
        self.display = pygame.display.set_mode()
        self.font = pygame.font.Font(
            os.path.join("D:", "\pythonCode", "Resources", "Fonts", "montserrat.ttf"),
            80,
        )
        self.font_size = self.font.get_ascent()
        self.box_x0, self.box_y0, self.x_margin, self.x_width = (
            box_x0,
            box_y0,
            x_margin,
            x_width,
        )


def build_text(msg):
    phraseFixed = ""
    words = [i["text"] for i in msg]
    while len(words) > 0:
        phraseScroll = " " * 50 + words[0]
        phraseScrollSurface = main.font.render(
            phraseScroll, True, (255, 255, 255), (0, 0, 0)
        )
        phraseFixedSurface = main.font.render(
            phraseFixed, True, (255, 255, 255), (0, 0, 0)
        )
        phraseScrollWidth = phraseScrollSurface.get_width()
        start_pos = 0
        while start_pos <= phraseScrollWidth:
            update_display(
                main.display,
                start_pos,
                phraseScrollWidth,
                phraseScrollSurface,
                phraseFixedSurface,
            )
            clock.tick()
            start_pos += 1
        phraseFixed += words[0][0]
        words = words[1:]


def update_display(display, t0, phraseScrollSurface, text_on=True, frame_on=True):
    display.fill((0, 0, 0))
    phraseScrollSurface = phraseScrollSurface.subsurface(
        (
            t0,
            0,
            min(main.x_width, phraseScrollSurface.get_width() - t0),
            main.font_size + 2,
        )
    )
    if text_on:
        display.blit(
            phraseScrollSurface,
            (main.box_x0 + main.x_margin, main.box_y0 + main.font_size // 3),
        )
    if frame_on:
        pygame.draw.rect(
            display,
            (24, 212, 212),
            (
                main.box_x0,
                main.box_y0,
                main.x_width + main.x_margin * 2,
                main.font_size * 2,
            ),
            width=9,
            border_radius=5,
        )
    pygame.display.update()


def test_scroll(msg):
    speed, start_wait, end_wait, start_cushion = (
        msg[0]["speed"],
        msg[0]["start_wait"],
        msg[0]["end_wait"],
        msg[0]["start_cushion"],
    )
    time.sleep(start_wait)
    fixed = ""
    for word in msg[1:]:
        text, keep = word["text"], word["keep"]
        phrase = " " * start_cushion + text
        for _ in range(len(phrase) - keep + 1):
            block = fixed + phrase + " " * 10
            phraseSurface = main.font.render(block, True, (255, 255, 255), (0, 0, 0))
            start_pos = 0
            update_display(
                main.display,
                start_pos,
                phraseSurface,
            )
            start_pos += 1
            if len(phrase) <= len(text):
                phrase = text[0:keep] + phrase[keep + 1 :]
            else:
                phrase = phrase[1:]
            time.sleep(speed)
        fixed += text[:keep]
    flicker(25, main.display, start_pos, phraseSurface)
    time.sleep(end_wait)


def flicker(repeat, display, start_pos, phraseSurface):
    for i, j in zip(
        f"{rnd.getrandbits(repeat):0b}",
        f"{rnd.getrandbits(repeat):0b}",
    ):
        text_on = True if i == "1" else False
        frame_on = True if j == "1" else False
        update_display(display, start_pos, phraseSurface, text_on, frame_on)
        time.sleep(rnd.randint(3, 8) / 20)
    update_display(display, start_pos, phraseSurface, text_on=True, frame_on=True)


def main():
    global main
    main = Main(box_x0=600, box_y0=600, x_margin=20, x_width=900)
    msg = [
        {"speed": 0.1, "start_wait": 0.5, "end_wait": 3, "start_cushion": 40},
        {"text": "AIR", "keep": 1},
        {"text": "TRAFFIC", "keep": 1},
        {"text": "CONTROL", "keep": 1},
        {"text": " SIMULATOR", "keep": 10},
    ]
    # build_text(msg)
    test_scroll(msg)


if __name__ == "__main__":
    main()
