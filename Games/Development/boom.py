import random
import pygame
from pygame.locals import *
import pygame_menu
from copy import deepcopy
from gft_utils import pygameUtils
import time

pygame.init()


class Game:
    def __init__(self):
        # load general presets
        pygameUtils.__init__(self)
        self.BACKGROUND = self.COLORS["GRAY"]

        # setup surfaces and sub-surfaces
        self.PLAY_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.6, self.DISPLAY_HEIGHT)
        )
        self.INFO_SURFACE = pygame.Surface(
            (self.DISPLAY_WIDTH * 0.4, self.DISPLAY_HEIGHT)
        )
        self.MSG_SURFACE = pygame.Surface(
            (self.INFO_SURFACE.get_width() * 0.8, self.INFO_SURFACE.get_height() * 0.4)
        )

        # setup entities
        self.COVERED_SQUARE = pygame.Surface((30, 30))
        self.COVERED_SQUARE.fill((100, 100, 100))
        self.UNCOVERED_SQUARE = pygame.Surface((30, 30))
        self.UNCOVERED_SQUARE.fill(self.BACKGROUND)
        self.FLAGGED_SQUARE = pygame.Surface((30, 30))
        self.FLAGGED_SQUARE.fill((200, 15, 12))
        # initial game parameters
        self.LEVEL_PRESETS = [
            (5, 5, 20, True),
            (12, 12, 25, True),
            (25, 25, 30, False),
            (40, 40, 40, False),
        ]
        self.grid_x = 20
        self.grid_y = 20
        self.bomb_density = 30
        self.uncover_one_at_start = True

    def setup(self):
        self.x0 = (self.PLAY_SURFACE.get_width() - 32 * self.grid_x) // 2
        self.y0 = (self.PLAY_SURFACE.get_height() - 32 * self.grid_y) // 2
        self.total_bombs = int(self.grid_x * self.grid_y * self.bomb_density / 100)
        flat = [False] * (self.grid_x * self.grid_y - self.total_bombs) + [
            True
        ] * self.total_bombs
        random.shuffle(flat)
        self.minefield_bombs = [
            flat[i : i + self.grid_x]
            for i in range(0, (self.grid_x * self.grid_y), self.grid_x)
        ]
        self.minefield_numbers = [
            [self.calculate_number(row, i) for i in range(self.grid_x)]
            for row in range(self.grid_y)
        ]
        self.minefield_uncovered = [[False] * self.grid_x for _ in range(self.grid_y)]
        self.minefield_marked = deepcopy(self.minefield_uncovered)
        # auto-uncover first square if option selected adn then neighbors
        if self.uncover_one_at_start:
            while True:
                i, row = random.randint(0, self.grid_x - 1), random.randint(
                    0, self.grid_y - 1
                )
                if (
                    self.minefield_numbers[row][i] == 0
                    and not self.minefield_bombs[row][i]
                ):
                    self.minefield_uncovered[row][i] = True
                    self.uncover_blank_neighbors()
                    break

        # create buttons
        self.B1POS = (2000, 1100)
        self.B1SFC = pygame.Surface((120, 80))
        self.B1SFC.fill((self.COLORS["LIGHT_BLUE"]))
        _text = self.FONTS["NUN40"].render("QUIT", True, self.COLORS["BLACK"])
        self.B1SFC.blit(source=_text, dest=_text.get_rect(center=(60, 40)))

    def calculate_number(self, y, x):
        bomb_count = 0
        for row in range(max(0, y - 1), min(self.grid_y - 1, y + 1) + 1):
            for i in range(max(0, x - 1), min(self.grid_x - 1, x + 1) + 1):
                if self.minefield_bombs[row][i] and not (i == x and row == y):
                    bomb_count += 1
        return bomb_count

    def update_display(self):
        # update PLAY surface
        self.PLAY_SURFACE.fill((50, 50, 50))
        for row in range(self.grid_y):
            for i in range(self.grid_x):
                _t = ""
                if self.minefield_uncovered[row][i]:
                    square = self.UNCOVERED_SQUARE.copy()
                    if self.minefield_numbers[row][i] > 0:
                        _t = str(self.minefield_numbers[row][i])
                    text = self.FONTS["NUN24"].render(
                        _t, True, self.COLORS["BLUE"], self.BACKGROUND
                    )
                    square.blit(source=text, dest=text.get_rect(center=(15, 15)))
                else:
                    if self.minefield_marked[row][i]:
                        square = self.FLAGGED_SQUARE.copy()
                    else:
                        square = self.COVERED_SQUARE.copy()

                self.PLAY_SURFACE.blit(
                    source=square, dest=(self.x0 + 32 * i, self.y0 + 32 * row)
                )
        self.MAIN_SURFACE.blit(source=self.PLAY_SURFACE, dest=(0, 0))

        # update INFO surface
        self.INFO_SURFACE.fill((75, 75, 75))
        self.messages = [f"Total Squares: {self.grid_x * self.grid_y}"]
        self.messages.append(f"Total Bombs: {self.total_bombs}")
        self.messages.append(
            f"Unmarked Bombs: {self.total_bombs-len([i for row in self.minefield_marked for i in row if i])}"
        )
        self.messages.append(
            f"Unopened Squares: {self.grid_x * self.grid_y-len([i for row in self.minefield_uncovered for i in row if i])}"
        )
        self.MSG_SURFACE.fill(self.COLORS["YELLOW"])
        for row, line in enumerate(self.messages):
            self.MSG_SURFACE.blit(
                self.FONTS["NUN40"].render(
                    line, True, self.COLORS["BLACK"], self.INFO_SURFACE.get_colorkey()
                ),
                dest=(10, row * 40),
            )

        self.INFO_SURFACE.blit(
            source=self.MSG_SURFACE, dest=(self.INFO_SURFACE.get_width() * 0.1, 20)
        )

        self.MAIN_SURFACE.blit(
            source=self.INFO_SURFACE, dest=(self.DISPLAY_WIDTH * 0.6, 0)
        )
        self.MAIN_SURFACE.blit(source=self.B1SFC, dest=self.B1POS)

        pygame.display.flip()

    def check_win(self):
        _uncovered = len([i for row in self.minefield_uncovered for i in row if not i])
        _marked = len([i for row in self.minefield_marked for i in row if i])
        if _uncovered == self.total_bombs and _uncovered == _marked:
            GAME.end_criteria = 1  # win game
            GAME.stage = 3

    def process_click(self, pos, button):
        if pygame.Rect(self.PLAY_SURFACE.get_rect()).collidepoint(
            pygame.mouse.get_pos()
        ):
            x0, y0 = pos[0] - self.x0, pos[1] - self.y0
            i, row = x0 // 32, y0 // 32

            # check if click in separation between squares
            if x0 % 32 > 30 or y0 % 32 > 30:
                return
            # check if click outside of square
            if i < 0 or i >= self.grid_x or row < 0 or row >= self.grid_y:
                return
            # check if square already uncovered
            if self.minefield_uncovered[row][i]:
                return

            # left-click: open square if not marked
            if button == 1 and not GAME.minefield_marked[row][i]:
                # check if mine there
                if GAME.minefield_bombs[row][i]:
                    GAME.end_criteria = 0  # lose game
                    GAME.stage = 3
                else:
                    GAME.minefield_uncovered[row][i] = True
                    self.uncover_blank_neighbors()

            # right-click: mark/unmark square
            elif button == 3 and not GAME.minefield_uncovered[row][i]:
                GAME.minefield_marked[row][i] = (
                    False if GAME.minefield_marked[row][i] else True
                )
        elif pygame.Rect(self.B1SFC.get_rect(topleft=GAME.B1POS)).collidepoint(pos):
            GAME.end_criteria = 2  # pressed QUIT button
            GAME.stage = 3

    def uncover_blank_neighbors(self):
        # uncover all squares adjacent to open blanks
        _change = True
        while _change:
            _change = False
            for row in range(self.grid_y):
                for i in range(self.grid_x):
                    if (
                        not GAME.minefield_numbers[row][i]
                        and GAME.minefield_uncovered[row][i]
                    ):
                        for y in range(
                            max(0, row - 1),
                            min(self.grid_y - 1, row + 1) + 1,
                        ):
                            for x in range(
                                max(0, i - 1),
                                min(self.grid_x - 1, i + 1) + 1,
                            ):
                                if not GAME.minefield_uncovered[y][x]:
                                    GAME.minefield_uncovered[y][x] = True
                                    _change = True

    def wrap_up(self):
        match self.end_criteria:
            case 0:  # Bomb Exploded (Lost)
                print("Boom!")
            case 1:  # Found all Bombs (Won)
                print("You Win!")
            case 2:  # QUIT button pressed
                print("Quitter...")


def main_menu():
    def set_game_parameters(value, parameter):
        val = int(value)
        match parameter:
            case 0:
                GAME.grid_x = val
            case 1:
                GAME.grid_y = val
            case 2:
                GAME.bomb_density = val
            case 3:
                GAME.uncover_one_at_start = val

    def start_game():
        GAME.stage = 1

    def press_preset_level(level):
        (
            GAME.grid_x,
            GAME.grid_y,
            GAME.bomb_density,
            GAME.uncover_one_at_start,
        ) = GAME.LEVEL_PRESETS[level]
        GAME.stage = 1

    MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
    MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
    MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()

    menu = pygame_menu.Menu(
        "Boom",
        600,
        800,
        theme=MENU_THEME,
        center_content=True,
        onclose=pygame_menu.events.CLOSE,
    )

    # define top frame
    frame1 = menu.add.frame_h(
        height=100, width=600, align=pygame_menu.locals.ALIGN_CENTER
    )
    frame1.set_title(" Preset Options")
    button_selection = (
        pygame_menu.widgets.SimpleSelection()
        .set_background_color(GAME.COLORS["BLACK"])
        .set_color(GAME.COLORS["BLUE"])
    )
    for level, text in enumerate(("Easy", "Medium", "Hard", "Expert")):
        b = menu.add.button(
            text,
            action=lambda: press_preset_level(level),
            padding=(5, 30),
            align=pygame_menu.locals.ALIGN_CENTER,
        )

        b.set_selection_effect(button_selection)
        frame1.pack(b)

    # define middle frame
    frame2 = menu.add.frame_v(height=300, width=600)
    frame2.set_title(" Manual Options")
    frame2.pack(
        menu.add.toggle_switch(
            f"{'Open Blank :':>27}",
            state_text=("No", "Yes"),
            onchange=lambda i: set_game_parameters(i, 3),
            default=GAME.uncover_one_at_start,
        )
    )
    frame2.pack(
        menu.add.range_slider(
            f"{'Horizontal Size :':>27}",
            range_values=(5, 40),
            increment=1,
            onchange=lambda i: set_game_parameters(i, 0),
            default=GAME.grid_x,
            value_format=lambda x: str(int(x)),
        )
    )
    frame2.pack(
        menu.add.range_slider(
            f"{'Vertical Size :':>30}",
            range_values=(5, 40),
            increment=1,
            default=GAME.grid_y,
            onchange=lambda i: set_game_parameters(i, 1),
            value_format=lambda x: str(int(x)),
        )
    )
    frame2.pack(
        menu.add.range_slider(
            f"{'Bomb Density % :':>23}",
            range_values=(20, 40),
            increment=1,
            default=GAME.bomb_density,
            onchange=lambda i: set_game_parameters(i, 2),
            value_format=lambda x: str(int(x)),
        )
    )

    frame3 = menu.add.frame_h(height=100, width=500)
    frame3.pack(
        menu.add.button("Play", action=start_game, padding=(5, 60), font_size=60)
    )

    return menu


def main():
    mainmenu = main_menu()
    GAME.stage = 0

    while mainmenu.is_enabled():
        match GAME.stage:
            case 0:
                mainmenu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            case 1:
                GAME.setup()
                GAME.stage = 2
            case 2:
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
                    GAME.update_display()
                    GAME.check_win()
            case 3:
                GAME.wrap_up()
                GAME.stage = 0


GAME = Game()
main()