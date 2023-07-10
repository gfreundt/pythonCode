import pygame
import os

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


def build_text(words):
    phraseFixed = ""
    while len(words) > 0:
        phraseScroll = " " * 50 + words[0]
        phraseScrollSurface = main.font.render(
            phraseScroll, True, (255, 255, 255), (0, 0, 0)
        )
        phraseFixedSurface = main.font.render(
            phraseFixed, True, (255, 255, 255), (0, 0, 0)
        )
        phraseWidth = phraseScrollSurface.get_width()
        start_pos = 0
        while start_pos <= phraseWidth:
            update_display(
                main.display,
                start_pos,
                phraseWidth,
                phraseScrollSurface,
                phraseFixedSurface,
            )
            clock.tick(300)
            start_pos += 1
        phraseFixed += words[0][0]
        words = words[1:]


def update_display(display, t0, t_width, phraseScrollSurface, phraseFixedSurface):
    display.fill((0, 0, 0))
    phraseScrollSurface = phraseScrollSurface.subsurface(
        (t0, 0, min(main.x_width, t_width - t0), main.font_size + 2)
    )
    display.blit(
        phraseScrollSurface,
        (main.box_x0 + main.x_margin, main.box_y0 + main.font_size // 3),
    )
    display.blit(
        phraseFixedSurface,
        (main.box_x0 + main.x_margin, main.box_y0 + main.font_size // 3),
    )
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


def main():
    global main
    main = Main(box_x0=200, box_y0=200, x_margin=20, x_width=900)
    build_text(["AIR TRAFFIC CONTROL SIMULATOR"])


if __name__ == "__main__":
    main()
