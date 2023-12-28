import pygame
from pygame.locals import *
import json
import pygame_menu


def menu(GAME):
    def set_game_parameters(value):
        GAME.parameters[int(menu.get_selected_widget()._id[-1])] = int(value)

    def start_game():
        GAME.stage = 1

    def press_preset_level():
        GAME.parameters = LEVEL_PRESETS[int(menu.get_selected_widget()._id[-1])].copy()
        # update widgets
        for k, widget in enumerate(widgets):
            if hasattr(widget, "_value"):
                widgets[k]._value = [GAME.parameters[k], 0]
            else:
                widgets[k]._state = GAME.parameters[k]

    # load game-specific initial parameters
    with open("game_parameters.json", mode="r") as file:
        init_values = json.load(file)[GAME.game]
        GAME.parameters = list(init_values["LEVEL_PRESETS"][0])
        LEVEL_PRESETS = init_values["LEVEL_PRESETS"]
        MENU_WIDTH, MENU_HEIGHT = init_values["MENU_WIDTH"], init_values["MENU_HEIGHT"]
        GAME_TITLE = init_values["GAME_TITLE"]
        WIDGETS = init_values["WIDGETS"]
    # load game high-scores
    with open("game_high_scores.json", mode="r") as file:
        GAME.HIGH_SCORES = json.load(file)[GAME.game]

    # fixed theme
    MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
    MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
    MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
    MENU_THEME.selection_color = GAME.PALETTE[2]

    menu = pygame_menu.Menu(
        GAME_TITLE,
        MENU_WIDTH,
        MENU_HEIGHT,
        theme=MENU_THEME,
        center_content=True,
        onclose=pygame_menu.events.CLOSE,
        position=(
            (GAME.MAIN_SURFACE.get_width() / 2 - MENU_WIDTH) / 2,
            (GAME.MAIN_SURFACE.get_height() - MENU_HEIGHT) / 2,
            False,
        ),
    )
    # define top frame
    frame1 = menu.add.frame_h(
        height=100, width=MENU_WIDTH, align=pygame_menu.locals.ALIGN_CENTER
    )
    frame1.set_title(
        " Preset Options",
        title_font_color=(GAME.COLORS["WHITE"]),
        background_color=(GAME.PALETTE[2]),
    )
    button_selection = pygame_menu.widgets.SimpleSelection().set_background_color(
        GAME.PALETTE[2]
    )
    for level, text in enumerate(("Easy", "Medium", "Hard", "Expert")):
        _b = menu.add.button(
            text,
            action=lambda: press_preset_level(),
            padding=(15, 30),
            font_color=GAME.PALETTE[2],
            selection_color=GAME.COLORS["WHITE"],
            align=pygame_menu.locals.ALIGN_CENTER,
            button_id="PRESET" + str(level),
        )
        _b.set_selection_effect(button_selection)
        frame1.pack(_b)

    # define middle frame
    frame2 = menu.add.frame_v(height=400, width=MENU_WIDTH)
    frame2.set_title(
        " Manual Options",
        title_font_color=(GAME.COLORS["WHITE"]),
        background_color=(GAME.PALETTE[2]),
    )
    widgets = []
    for k, w in enumerate(WIDGETS):
        if w["type"] == "slider":
            _widget = menu.add.range_slider(
                f'{w["name"]:>27}',
                range_values=w["range"],
                padding=(24, 0, 0, w["padding"]),
                increment=w["increment"],
                font_color=GAME.PALETTE[2],
                range_line_height=3,
                range_text_value_color=GAME.COLORS["BLACK"],
                slider_color=GAME.COLORS["BLACK"],
                slider_selected_color=GAME.COLORS["BLACK"],
                slider_text_value_bgcolor=GAME.PALETTE[1],
                slider_text_value_color=GAME.COLORS["WHITE"],
                range_line_color=GAME.COLORS["BLACK"],
                range_text_value_tick_color=GAME.COLORS["BLACK"],
                range_text_value_tick_thick=3,
                onchange=lambda i: set_game_parameters(i),
                default=GAME.parameters[k],
                value_format=lambda x: str(int(x)),
                rangeslider_id="WIDGET" + str(k),
            )
        elif w["type"] == "switch":
            _widget = menu.add.toggle_switch(
                w["name"],
                padding=(24, 0, 0, w["padding"]),
                font_color=GAME.PALETTE[2],
                state_color=(GAME.PALETTE[2], (255, 255, 255)),
                state_text_font_color=((255, 255, 255), GAME.PALETTE[2]),
                state_text=("No", "Yes"),
                onchange=lambda i: set_game_parameters(i),
                default=GAME.parameters[k],
                width=70,
                slider_thickness=0,
                toggleswitch_id="WIDGET" + str(k),
            )
        widgets.append(_widget)
        frame2.pack(_widget)

    # bottom "frame"
    _b = menu.add.button(
        " PLAY ",
        font_name=pygame_menu.font.FONT_DIGITAL,
        font_color=(38, 158, 151),
        action=start_game,
        font_size=60,
        align=pygame_menu.locals.ALIGN_CENTER,
    )
    _b.set_background_color(color=(4, 47, 58))
    _b._font_selected_color = GAME.COLORS["WHITE"]

    return menu


def show_high_scores(GAME):
    _title = GAME.FONTS["NUN80B"].render(
        "High Scores",
        True,
        GAME.COLORS["WHITE"],
        GAME.RIGHT_SURFACE.get_colorkey(),
    )
    GAME.RIGHT_SURFACE.blit(
        _title, dest=((GAME.RIGHT_SURFACE.get_width() - _title.get_width()) / 2, 60)
    )

    for k, _score in enumerate(GAME.HIGH_SCORES):
        _row = [
            f"{_score['player']:<20}",
            f"{_score['score']:>10}",
            f"{_score['time']}",
            f"{_score['date']}",
        ]
        for j, _item in enumerate(_row):
            _text = GAME.FONTS["NUN40"].render(
                _item,
                True,
                GAME.COLORS["WHITE"],
                GAME.RIGHT_SURFACE.get_colorkey(),
            )
            GAME.RIGHT_SURFACE.blit(
                _text,
                dest=(
                    (GAME.RIGHT_SURFACE.get_width() - _text.get_width()) / 2 + j * 150,
                    160 + 60 * k,
                ),
            )

    GAME.MAIN_SURFACE.blit(
        GAME.RIGHT_SURFACE, dest=(GAME.MAIN_SURFACE.get_width() / 2, 0)
    )
    pygame.display.flip()


def define_main_surfaces(GAME):
    GAME.PLAY_SURFACE = pygame.Surface((GAME.DISPLAY_WIDTH * 0.6, GAME.DISPLAY_HEIGHT))
    GAME.INFO_SURFACE = pygame.Surface((GAME.DISPLAY_WIDTH * 0.4, GAME.DISPLAY_HEIGHT))
    GAME.MSG_SURFACE = pygame.Surface(
        (
            GAME.INFO_SURFACE.get_width() * 0.8,
            GAME.INFO_SURFACE.get_height() * 0.265,
        )
    )


def main_game_button(GAME, button_text):
    _text = GAME.FONTS["NUN40B"].render(button_text, True, GAME.COLORS["WHITE"])
    _sfc = pygame.Surface((_text.get_width() * 1.25, 80))
    _sfc.fill(GAME.PALETTE[4])
    _sfc.blit(source=_text, dest=_text.get_rect(center=(_text.get_width() * 0.625, 40)))
    _pos = (
        GAME.PLAY_SURFACE.get_width()
        + (GAME.INFO_SURFACE.get_width() - _sfc.get_width()) // 2,
        1150,
    )
    GAME.main_button = (_sfc, _pos)


def load_generic_images(GAME):
    GAME.end_images = {
        "lost": pygame.image.load("game_lost.png"),
        "won": pygame.image.load("game_won.png"),
        "quit": pygame.image.load("game_quit.png"),
    }


def check_if_main_game_button_pressed(GAME, pos):
    # clicked on control button
    if pygame.Rect(
        GAME.main_button[0].get_rect(topleft=GAME.main_button[1])
    ).collidepoint(pos):
        GAME.end_criteria = "quit"
        GAME.stage = 3


def update_info_surface(GAME, message):
    # update INFO surface
    GAME.INFO_SURFACE.fill(GAME.PALETTE[2])

    # print crafted text
    GAME.MSG_SURFACE.fill(GAME.COLORS["BLACK"])
    for row, line in enumerate(message):
        if not line[0]:
            line = ("", "", "NUN40")
        GAME.MSG_SURFACE.blit(
            GAME.FONTS[line[2]].render(
                line[0],
                True,
                GAME.COLORS["WHITE"],
                GAME.INFO_SURFACE.get_colorkey(),
            ),
            dest=(60, row * 40),
        )
        GAME.MSG_SURFACE.blit(
            GAME.FONTS[line[2]].render(
                line[1],
                True,
                GAME.COLORS["WHITE"],
                GAME.INFO_SURFACE.get_colorkey(),
            ),
            dest=(400, row * 40),
        )

    GAME.INFO_SURFACE.blit(
        source=GAME.MSG_SURFACE, dest=(GAME.INFO_SURFACE.get_width() * 0.1, 90)
    )
    # exit image
    if GAME.stage == 3:
        GAME.INFO_SURFACE.blit(
            source=GAME.end_images[GAME.end_criteria], dest=(240, 560)
        )
    GAME.MAIN_SURFACE.blit(source=GAME.INFO_SURFACE, dest=(GAME.DISPLAY_WIDTH * 0.6, 0))
    # main game button
    GAME.MAIN_SURFACE.blit(source=GAME.main_button[0], dest=GAME.main_button[1])


def wrap_up(GAME):
    main_game_button(GAME, " CONTINUE ")
    GAME.update_display()
    while True:
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONDOWN and pygame.Rect(
                GAME.main_button[0].get_rect(topleft=GAME.main_button[1])
            ).collidepoint(pygame.mouse.get_pos()):
                return


def main(GAME):
    clock = pygame.time.Clock()
    GAME.stage = 0
    main_menu = menu(GAME)
    while main_menu.is_enabled():
        match GAME.stage:
            case 0:
                GAME.FPS = 60  # low frame rate for menu
                main_menu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
                show_high_scores(GAME)
            case 1:
                GAME.setup()
                GAME.stage = 2
            case 2:
                GAME.FPS = 60  # higher frame rate for game
                GAME.update_display()
                events = pygame.event.get()
                for event in events:
                    if event.type == QUIT or (
                        event.type == KEYDOWN and event.key == 27
                    ):
                        GAME.end_criteria = "quit"
                        GAME.stage = 3
                    elif event.type == KEYDOWN:
                        GAME.process_key(key=event.key)
                    elif event.type == MOUSEBUTTONDOWN:
                        GAME.process_click(
                            pos=pygame.mouse.get_pos(), button=event.button
                        )
                GAME.check_end()
                clock.tick(GAME.FPS)
            case 3:
                GAME.wrap_up()
                GAME.stage = 0

    pygame.quit()
