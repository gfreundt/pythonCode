from pygame.locals import *
import sys, os
import subprocess
import json
import pygame_menu

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils


class Game:
    def __init__(self):
        # self.app = os.path.split(sys.argv[0])[1].split(".")[0]
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
        # load game-specific initial parameters
        with open("game_parameters.json", mode="r") as file:
            self.GAME_DATA = dict(sorted(json.load(file).items()))
            self.GAME_LIST = [i for i in self.GAME_DATA]
        # other variables
        self.launch = False

    def press_preset_level(self):
        pass

    def set_self_parameters(self):
        pass

    def start_self(self):
        self.launch = True
        main_menu.close()

    def select_game(self):
        self.selection = GAME.GAME_LIST[int(main_menu.get_selected_widget()._id[4:])]

    def menu(self):
        MENU_WIDTH = 1000
        MENU_HEIGHT = 1400

        # fixed theme
        MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
        MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
        MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
        MENU_THEME.selection_color = self.PALETTE[2]

        menu = pygame_menu.Menu(
            "Launchgr",
            MENU_WIDTH,
            MENU_HEIGHT,
            theme=MENU_THEME,
            center_content=True,
            onclose=pygame_menu.events.CLOSE,
            position=(
                (self.MAIN_SURFACE.get_width() / 2 - MENU_WIDTH) / 2,
                (self.MAIN_SURFACE.get_height() - MENU_HEIGHT) / 2,
                False,
            ),
        )

        # define top frame
        frame1 = menu.add.frame_h(
            height=100, width=MENU_WIDTH, align=pygame_menu.locals.ALIGN_CENTER
        )
        frame1.set_title(
            " Preset Options",
            title_font_color=(self.COLORS["WHITE"]),
            background_color=(self.PALETTE[2]),
        )
        button_selection = pygame_menu.widgets.SimpleSelection().set_background_color(
            self.PALETTE[2]
        )
        for level, text in enumerate(("Easy", "Medium", "Hard", "Expert")):
            _b = menu.add.button(
                text,
                action=lambda: self.press_preset_level(),
                padding=(15, 30),
                font_color=self.PALETTE[2],
                selection_color=self.COLORS["WHITE"],
                align=pygame_menu.locals.ALIGN_CENTER,
                button_id="PRESET" + str(level),
            )
            _b.set_selection_effect(button_selection)
            frame1.pack(_b)

        # define middle frame
        frame2 = menu.add.frame_v(height=800, width=MENU_WIDTH)
        frame2.set_title(
            " Available Games",
            title_font_color=(self.COLORS["WHITE"]),
            background_color=(self.PALETTE[2]),
        )
        _col_size = max([len(i) for i in self.GAME_DATA])
        for k, w in enumerate(self.GAME_DATA):
            _version = self.GAME_DATA[w]["VERSION"]
            _widget = menu.add.button(
                f" {(w+' ').title():-<{_col_size+5}} V{str(_version)}",
                padding=(10, 10, 10, 10),
                font_color=self.COLORS["MAROON"] if _version < 1 else self.PALETTE[2],
                action=self.select_game,
                selection_color=self.COLORS["WHITE"],
                button_id="GAME" + str(k),
            )
            _widget.set_selection_effect(button_selection)
            frame2.pack(_widget)

        # bottom "frame"
        _b = menu.add.button(
            " PLAY ",
            font_name=pygame_menu.font.FONT_DIGITAL,
            font_color=(38, 158, 151),
            action=self.start_self,
            font_size=60,
            align=pygame_menu.locals.ALIGN_CENTER,
        )
        _b.set_background_color(color=(4, 47, 58))
        _b._font_selected_color = self.COLORS["WHITE"]

        return menu


if __name__ == "__main__":
    GAME = Game()
    main_menu = GAME.menu()
    GAME.FPS = 10  # low frame rate for menu
    main_menu.mainloop(GAME.MAIN_SURFACE)
    if GAME.launch:
        _py_file = GAME.GAME_DATA[GAME.selection]["APP"]
        _user = "Superman"
        subprocess.run(["python", _py_file, _user])
