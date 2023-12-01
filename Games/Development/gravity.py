import random
import pygame
from pygame.locals import *
import sys, os
from copy import deepcopy as copy
import math

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import menus

pygame.init()


class Game:
    def __init__(self):
        # load general presets
        pygameUtils.__init__(self)

        # define pallette
        self.COLOR_LIST = [
            self.COLORS["BLACK"],
            self.COLORS["YELLOW"],
            self.COLORS["GREEN"],
            self.COLORS["BLUE"],
            self.COLORS["RED"],
            self.COLORS["GRAY"],
            self.COLORS["GRAY"],
        ]
        # setup surfaces and sub-surfaces

        pygame.display.set_caption("Mastermind")
        self.PLAY_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.6, self.DISPLAY_HEIGHT)
        )
        self.INFO_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.4, self.DISPLAY_HEIGHT * 0.5)
        )
        self.MSG_SURFACE = pygame.Surface(
            (self.INFO_SURFACE.get_width() * 0.8, self.INFO_SURFACE.get_height() * 0.4)
        )
        self.PLAYx, self.PLAYy = (200, 200)
        self.path = []
        self.path_draw_step = 0
        self.FPS = 60

    def setup(self):
        self.MAIN_SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

        self.gravity = 9.8  # m/s2
        self.wind = 4  # m/s

        self.source_loc = (100, 1000)
        self.x, self.y = (100, 1000)
        self.target_loc = (1500, 900)

        self.xVel = self._speed * math.sin(math.radians(self._angle))
        self.yVel = self._speed * -math.cos(math.radians(self._angle))

    def update_display(self):
        self.MAIN_SURFACE.fill(self.COLORS["GRAY"])
        floor = pygame.draw.line(
            self.MAIN_SURFACE,
            self.COLORS["BLACK"],
            (50, 1100),
            (2500, 1100),
        )

        self.target = pygame.draw.circle(
            self.MAIN_SURFACE,
            color=self.COLORS["RED"],
            center=self.target_loc,
            radius=10,
        )
        self.origin = pygame.draw.circle(
            self.MAIN_SURFACE,
            color=self.COLORS["GREEN"],
            center=self.source_loc,
            radius=10,
        )

        [
            pygame.draw.circle(
                self.MAIN_SURFACE, color=self.COLORS["BLACK"], center=(x, y), radius=1
            )
            for (x, y) in self.path
        ]

        if self.path_draw_step % 3 == 0:
            self.path.append((self.x, self.y))
        self.path_draw_step += 1

        self.update_coordinates()
        self.source = pygame.draw.circle(
            self.MAIN_SURFACE,
            color=self.COLORS["BLUE"],
            center=(self.x, self.y),
            radius=10,
        )
        pygame.display.flip()

    def update_coordinates(self):
        self.x += self.xVel * (1 / self.FPS)
        self.y += self.yVel * (1 / self.FPS)
        self.yVel += self.gravity * (1 / self.FPS)
        self.xVel += self.wind * (1 / self.FPS)

    def check_win(self):
        if pygame.Rect.colliderect(self.source, self.target):
            GAME.stage = 3
        if self.x > self.DISPLAY_WIDTH or self.y > self.DISPLAY_HEIGHT:
            GAME.stage = 3

    def wrap_up(self):
        pygame.quit()


def main():
    global GAME
    GAME = Game()
    GAME.stage = 0  # change to 0
    # main_menu = menus.mastermind(GAME)

    clock = pygame.time.Clock()
    while True:  # main_menu.is_enabled():
        match GAME.stage:
            case 0:
                GAME._speed = int(input("Speed: "))
                GAME._angle = int(input("Angle: "))
                GAME.stage = 1

                # main_menu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            case 1:
                GAME.setup()
                GAME.stage = 2
            case 2:
                GAME.update_display()
                events = pygame.event.get()
                for event in events:
                    if event.type == QUIT or (
                        event.type == KEYDOWN and event.key == 27
                    ):
                        GAME.stage = 3
                    elif event.type == MOUSEBUTTONDOWN:
                        GAME.process_click(
                            pos=pygame.mouse.get_pos(), button=event.button
                        )
                GAME.check_win()
                clock.tick(GAME.FPS)
            case 3:
                GAME.wrap_up()
                GAME.stage = 0


if __name__ == "__main__":
    main()
