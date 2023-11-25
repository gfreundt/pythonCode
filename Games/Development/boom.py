import random
import pygame
from pygame.locals import *
import pygame_menu
from copy import deepcopy
import sys, os

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
        self.COLOR1 = self.COLORS["CYBER_BLUE01"]
        self.COLOR2 = self.COLORS["CYBER_BLUE02"]
        self.COLOR3 = self.COLORS["CYBER_BLUE03"]
        self.COLOR4 = self.COLORS["CYBER_BLUE04"]
        self.COLOR5 = self.COLORS["CYBER_BLUE05"]
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
        # create all possible squares
        self.COVERED_SQUARE = pygame.Surface((30, 30))
        self.COVERED_SQUARE.fill(self.COLOR3)
        self.UNCOVERED_SQUARE = self.COVERED_SQUARE.copy()
        self.UNCOVERED_SQUARE.fill(self.COLOR1)
        self.FLAGGED_SQUARE = self.COVERED_SQUARE.copy()
        self.FLAGGED_SQUARE.fill(self.COLORS["MAROON"])
        self.BOMB2_SQUARE = self.COVERED_SQUARE.copy()
        self.BOMB2_SQUARE.fill(self.COLORS["DARK_MAROON"])
        self.BOMB1_SQUARE = self.FLAGGED_SQUARE.copy()
        pygame.draw.line(
            self.BOMB1_SQUARE, self.COLORS["GRAY"], (0, 0), (30, 30), width=3
        )
        pygame.draw.line(
            self.BOMB1_SQUARE, self.COLORS["GRAY"], (30, 0), (0, 30), width=3
        )

        self.B1POS = (2000, 1100)

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
        # auto-uncover first square if option selected and then neighbors
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

        # create main game button
        self.main_game_button(" QUIT ")

    def main_game_button(self, text):
        _text = self.FONTS["NUN40"].render(text, True, self.COLORS["BLACK"])
        self.B1SFC = pygame.Surface((_text.get_width(), 80))
        self.B1SFC.fill(self.COLOR3)
        self.B1SFC.blit(
            source=_text, dest=_text.get_rect(center=(_text.get_width() // 2, 40))
        )

    def calculate_number(self, y, x):
        bomb_count = 0
        for row in range(max(0, y - 1), min(self.grid_y - 1, y + 1) + 1):
            for i in range(max(0, x - 1), min(self.grid_x - 1, x + 1) + 1):
                if self.minefield_bombs[row][i] and not (i == x and row == y):
                    bomb_count += 1
        return bomb_count

    def update_display(self):
        # update PLAY surface
        self.PLAY_SURFACE.fill((15, 15, 15))
        for row in range(self.grid_y):
            for i in range(self.grid_x):
                _t = ""
                if self.minefield_uncovered[row][i] or self.reveal:
                    square = self.UNCOVERED_SQUARE.copy()
                    if self.minefield_numbers[row][i] > 0:
                        _t = str(self.minefield_numbers[row][i])
                    text = self.FONTS["NUN24"].render(
                        _t, True, self.COLORS["BLACK"], self.COLOR1
                    )
                    square.blit(source=text, dest=text.get_rect(center=(15, 15)))
                else:
                    if self.minefield_marked[row][i]:
                        square = self.FLAGGED_SQUARE.copy()
                    else:
                        square = self.COVERED_SQUARE.copy()

                if self.reveal:
                    if (
                        self.minefield_bombs[row][i] and self.minefield_marked[row][i]
                    ):  # square flagged correctly
                        square = self.FLAGGED_SQUARE.copy()
                    elif (
                        not self.minefield_bombs[row][i]
                        and self.minefield_marked[row][i]
                    ):  # square flagged incorrectly
                        square = self.BOMB1_SQUARE.copy()
                    elif (
                        self.minefield_bombs[row][i]
                        and not self.minefield_marked[row][i]
                    ):  # square not flagged
                        square = self.BOMB2_SQUARE.copy()

                self.PLAY_SURFACE.blit(
                    source=square, dest=(self.x0 + 32 * i, self.y0 + 32 * row)
                )
        self.MAIN_SURFACE.blit(source=self.PLAY_SURFACE, dest=(0, 0))

        # update INFO surface
        self.INFO_SURFACE.fill(self.COLOR1)
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
        # TODO: do not uncover if marked

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
                GAME.reveal = True
            case 1:  # Found all Bombs (Won)
                print("You Win!")
            case 2:  # QUIT button pressed
                print("Quitter...")

        self.main_game_button(" CONTINUE ")
        self.update_display()
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN and pygame.Rect(
                    self.B1SFC.get_rect(topleft=GAME.B1POS)
                ).collidepoint(pygame.mouse.get_pos()):
                    return


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

    def press_preset_level():
        (
            GAME.grid_x,
            GAME.grid_y,
            GAME.bomb_density,
            GAME.uncover_one_at_start,
        ) = GAME.LEVEL_PRESETS[int(menu.get_selected_widget()._id)]
        # update widgets
        GAME.widgets[0]._value = [GAME.grid_x, 0]
        GAME.widgets[1]._value = [GAME.grid_y, 0]
        GAME.widgets[2]._value = [GAME.bomb_density, 0]
        GAME.widgets[3]._state = GAME.uncover_one_at_start

    def draw_widgets():
        # define top frame
        frame1 = menu.add.frame_h(
            height=100, width=600, align=pygame_menu.locals.ALIGN_CENTER
        )
        frame1.set_title(
            " Preset Options",
            title_font_color=(GAME.COLORS["WHITE"]),
            background_color=(GAME.COLOR3),
        )
        button_selection = pygame_menu.widgets.SimpleSelection().set_background_color(
            GAME.COLOR3
        )
        for level, text in enumerate(("Easy", "Medium", "Hard", "Expert")):
            _b = menu.add.button(
                text,
                action=lambda: press_preset_level(),
                padding=(15, 30),
                font_color=GAME.COLOR3,
                selection_color=GAME.COLORS["WHITE"],
                align=pygame_menu.locals.ALIGN_CENTER,
                button_id=str(level),
            )

            _b.set_selection_effect(button_selection)
            frame1.pack(_b)

        # define middle frame
        frame2 = menu.add.frame_v(height=400, width=600)
        frame2.set_title(
            " Manual Options",
            title_font_color=(GAME.COLORS["WHITE"]),
            background_color=(GAME.COLOR3),
        )

        GAME.widgets = [
            menu.add.range_slider(
                f"{'Horizontal Size :':>27}",
                range_values=(5, 40),
                padding=(22, 0, 0, 1),
                increment=1,
                font_color=GAME.COLOR3,
                range_line_height=3,
                range_text_value_color=GAME.COLORS["BLACK"],
                slider_color=GAME.COLORS["BLACK"],
                slider_selected_color=GAME.COLORS["BLACK"],
                slider_text_value_bgcolor=GAME.COLOR2,
                slider_text_value_color=GAME.COLORS["WHITE"],
                range_line_color=GAME.COLORS["BLACK"],
                range_text_value_tick_color=GAME.COLORS["BLACK"],
                range_text_value_tick_thick=3,
                onchange=lambda i: set_game_parameters(i, 0),
                default=GAME.grid_x,
                value_format=lambda x: str(int(x)),
            )
        ]
        GAME.widgets.append(
            menu.add.range_slider(
                "Vertical Size :",
                range_values=(5, 40),
                padding=(24, 0, 0, 121),
                increment=1,
                font_color=GAME.COLOR3,
                range_line_height=3,
                range_text_value_color=GAME.COLORS["BLACK"],
                slider_color=GAME.COLORS["BLACK"],
                slider_selected_color=GAME.COLORS["BLACK"],
                slider_text_value_bgcolor=GAME.COLOR2,
                slider_text_value_color=GAME.COLORS["WHITE"],
                range_line_color=GAME.COLORS["BLACK"],
                range_text_value_tick_color=GAME.COLORS["BLACK"],
                range_text_value_tick_thick=3,
                default=GAME.grid_y,
                onchange=lambda i: set_game_parameters(i, 1),
                value_format=lambda x: str(int(x)),
            )
        )
        GAME.widgets.append(
            (
                menu.add.range_slider(
                    "Bomb Density % :",
                    range_values=(10, 30),
                    padding=(24, 0, 0, 60),
                    increment=1,
                    font_color=GAME.COLOR3,
                    default=GAME.bomb_density,
                    range_line_height=3,
                    range_text_value_color=GAME.COLORS["BLACK"],
                    slider_color=GAME.COLORS["BLACK"],
                    slider_selected_color=GAME.COLORS["BLACK"],
                    slider_text_value_bgcolor=GAME.COLOR2,
                    slider_text_value_color=GAME.COLORS["WHITE"],
                    range_line_color=GAME.COLORS["BLACK"],
                    range_text_value_tick_color=GAME.COLORS["BLACK"],
                    range_text_value_tick_thick=3,
                    onchange=lambda i: set_game_parameters(i, 2),
                    value_format=lambda x: str(int(x)),
                )
            )
        )
        GAME.widgets.append(
            (
                menu.add.toggle_switch(
                    "Open Blank at Start :",
                    padding=(30, 0, 0, 100),
                    font_color=GAME.COLOR3,
                    state_color=(GAME.COLOR3, (255, 255, 255)),
                    state_text_font_color=((255, 255, 255), GAME.COLOR3),
                    state_text=("No", "Yes"),
                    onchange=lambda i: set_game_parameters(i, 3),
                    default=GAME.uncover_one_at_start,
                    width=70,
                    slider_thickness=0,
                )
            )
        )
        for widget in GAME.widgets:
            frame2.pack(widget)

        _b = menu.add.button(
            " PLAY ",
            font_color=(38, 158, 151),
            action=start_game,
            font_size=60,
            align=pygame_menu.locals.ALIGN_CENTER,
        )

        _b.set_background_color(color=(4, 47, 58))
        _b._font_selected_color = GAME.COLORS["WHITE"]

    MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
    MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
    MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
    MENU_THEME.selection_color = GAME.COLOR3

    menu = pygame_menu.Menu(
        "Boom",
        600,
        800,
        theme=MENU_THEME,
        center_content=True,
        onclose=pygame_menu.events.CLOSE,
    )

    draw_widgets()
    return menu


def main():
    GAME.stage = 0
    main_menu = menus.boom(GAME)
    while main_menu.is_enabled():
        match GAME.stage:
            case 0:
                main_menu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            case 1:
                GAME.reveal = False
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
