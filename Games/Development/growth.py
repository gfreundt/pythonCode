import pygame
from pygame.locals import *
from random import randrange, choice
import sys, os
from datetime import datetime as dt
from datetime import timedelta as td
import time
from copy import deepcopy as copy

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils
import game_shell as shell

pygame.init()


class Sprite(pygame.sprite.Sprite):
    def __init__(self, color, width, height, x0, y0):
        super().__init__()
        self.color = color
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x0
        self.rect.y = y0


class Game:
    def __init__(self, game_name):
        self.game = game_name
        # load general presets
        pygameUtils.__init__(self)
        # load palette and colors
        self.PALETTE = self.PALETTES["CYBER_BLUE"]
        self.COLOR_OPTIONS = [
            self.COLORS["MAROON"],
            self.COLORS["BLUE"],
            self.COLORS["RED"],
            self.COLORS["GREEN"],
            self.COLORS["LIGHT_BLUE"],
        ]
        # setup surfaces and sub-surfaces
        shell.define_main_surfaces(self)
        # load images
        shell.load_generic_images(self)
        # sprites grouping
        self.all_sprites = pygame.sprite.Group()
        self.all_hunters = pygame.sprite.Group()

    def setup(self):
        # assign generic menu parameters to game-specific variables
        (
            self.max_value,
            self.MAX_CAPTURE,
            self.MAX_SIZE,
            self.reload_sprites,
        ) = self.parameters
        self.MAX_TIME = 60
        # initial values
        self.score = 0
        self.hunter_width = randrange(10, 31)
        self.hunter_height = int(self.hunter_width)
        self.hunter = Sprite(
            color=self.COLORS["YELLOW"],
            width=self.hunter_width,
            height=self.hunter_height,
            x0=500,
            y0=500,
        )
        self.hunter_value = 0
        self.hunter_deltax, self.hunter_deltay = 0, 0
        self.all_hunters.add(self.hunter)
        self.EDGES = {
            "left": 0,
            "right": self.PLAY_SURFACE.get_width() - self.hunter_width,
            "top": 0,
            "bottom": self.PLAY_SURFACE.get_height() - self.hunter_height,
        }
        self.collected_sprites = 0
        # random blocks of varying size and value
        _counter = 0
        while _counter < 60:  # TODO: update to vraible
            _block = Sprite(
                color=choice(self.COLOR_OPTIONS),
                width=randrange(20, self.MAX_SIZE),
                height=randrange(20, self.MAX_SIZE),
                x0=randrange(50, 1500),
                y0=randrange(50, 1200),
            )
            # ignore new block if it collides with existing block
            if pygame.sprite.spritecollideany(
                _block, self.all_sprites
            ) or pygame.sprite.spritecollideany(_block, self.all_hunters):
                continue
            # render value in block
            _block.value = randrange(1, self.max_value)
            _text = self.FONTS["NUN24"].render(
                str(_block.value), True, self.COLORS["WHITE"], _block.color
            )
            _block.image.blit(
                source=_text,
                dest=_text.get_rect(center=(_block.width // 2, _block.height // 2)),
            )
            self.all_sprites.add(_block)
            _counter += 1

        # create main game button
        shell.main_game_button(self, "QUIT")
        # start timer
        self.time_start = dt.now()

    def next_turn(self):
        self.hunter.rect.x += self.hunter_deltax
        self.hunter.rect.y += self.hunter_deltay

        collision = pygame.sprite.spritecollide(
            self.hunter, self.all_sprites, dokill=True
        )
        if collision:
            self.hunter_value += sum(i.value for i in collision)
            self.collected_sprites += 1

    def update_display(self):
        self.next_turn()
        self.MAIN_SURFACE.fill(self.COLORS["BLACK"])
        # self.all_sprites.update()
        self.all_sprites.draw(self.MAIN_SURFACE)
        self.all_hunters.draw(self.MAIN_SURFACE)
        _message = [
            ("Board Statistics", "", "NUN40B"),
            ("Score", f"< {self.hunter_value} >", "NUN40"),
            (
                "Time",
                f"< {(dt.now() - self.time_start).total_seconds():.1f} seconds >",
                "NUN40",
            ),
        ]
        shell.update_info_surface(GAME, _message)
        pygame.display.flip()

    def rotate_head(self):
        pass

    def process_click(self, pos, button):
        # clicked on control button
        if shell.check_if_main_game_button_pressed(self, pos):
            return

    def process_key(self, key):
        if key == K_RIGHT:
            self.hunter_deltax += 1
        elif key == K_LEFT:
            self.hunter_deltax -= 1
        if key == K_UP:
            self.hunter_deltay -= 1
        elif key == K_DOWN:
            self.hunter_deltay += 1

    def check_end(self):
        # time is up
        if (dt.now() - self.time_start).total_seconds() > self.MAX_TIME:
            self.stage = 3
            self.end_criteria = "won"
        # hunter gone off-limits
        if (
            self.hunter.rect.x < self.EDGES["left"]
            or self.hunter.rect.x > self.EDGES["right"]
            or self.hunter.rect.y < self.EDGES["top"]
            or self.hunter.rect.y > self.EDGES["bottom"]
        ):
            self.stage = 3
            self.end_criteria = "lost"
        # reached maximum amount of sprites collected
        if self.collected_sprites >= self.MAX_CAPTURE:
            self.stage = 3
            self.end_criteria = "won"

    def wrap_up(self):
        shell.wrap_up(GAME)

    def high_score(self):
        if self.end_criteria == "won":
            self.score = self.hunter_value
            shell.update_high_scores(self)


if __name__ == "__main__":
    GAME = Game("growth")
    shell.main(GAME)
    pygame.quit()
