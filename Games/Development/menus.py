import win32gui
import pygame
from pygame.locals import *
import pygame_menu

pygame.init()


def boom(GAME):
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
        ) = LEVEL_PRESETS[int(menu.get_selected_widget()._id)]
        # update widgets
        GAME.widgets[0]._value = [GAME.grid_x, 0]
        GAME.widgets[1]._value = [GAME.grid_y, 0]
        GAME.widgets[2]._value = [GAME.bomb_density, 0]
        GAME.widgets[3]._state = GAME.uncover_one_at_start

    LEVEL_PRESETS = [
        (5, 5, 10, True),
        (12, 12, 15, True),
        (25, 25, 20, False),
        (40, 40, 30, False),
    ]
    (
        GAME.grid_x,
        GAME.grid_y,
        GAME.bomb_density,
        GAME.uncover_one_at_start,
    ) = LEVEL_PRESETS[0]
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

    # bottom "frame"
    _b = menu.add.button(
        " PLAY ",
        font_color=(38, 158, 151),
        action=start_game,
        font_size=60,
        align=pygame_menu.locals.ALIGN_CENTER,
    )

    _b.set_background_color(color=(4, 47, 58))
    _b._font_selected_color = GAME.COLORS["WHITE"]

    return menu


def liquids(GAME):
    def set_game_parameters(value, parameter):
        val = int(value)
        match parameter:
            case 0:
                GAME.full_bottles = val
            case 1:
                GAME.empty_bottles = val
            case 2:
                GAME.bottle_size = val
            case 3:
                GAME.colors = val

    def start_game():
        GAME.stage = 1

    def press_preset_level():
        (
            GAME.full_bottles,
            GAME.empty_bottles,
            GAME.bottle_size,
            GAME.colors,
        ) = LEVEL_PRESETS[int(menu.get_selected_widget()._id)]
        # update widgets
        GAME.widgets[0]._value = [GAME.full_bottles, 0]
        GAME.widgets[1]._value = [GAME.empty_bottles, 0]
        GAME.widgets[2]._value = [GAME.bottle_size, 0]
        GAME.widgets[3]._state = [GAME.colors, 0]

    LEVEL_PRESETS = [(12, 3, 4, 2), (20, 2, 5, 3), (38, 2, 6, 4), (50, 1, 6, 5)]
    (
        GAME.full_bottles,
        GAME.empty_bottles,
        GAME.bottle_size,
        GAME.colors,
    ) = LEVEL_PRESETS[0]

    MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
    MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
    MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
    MENU_THEME.selection_color = GAME.COLOR3

    menu = pygame_menu.Menu(
        "Liquids",
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
            f"{'Full Bottles :':>27}",
            range_values=(8, 50),
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
            default=GAME.full_bottles,
            value_format=lambda x: str(int(x)),
        )
    ]
    GAME.widgets.append(
        menu.add.range_slider(
            "Empty Bottles :",
            range_values=(1, 4),
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
            default=GAME.empty_bottles,
            onchange=lambda i: set_game_parameters(i, 1),
            value_format=lambda x: str(int(x)),
        )
    )
    GAME.widgets.append(
        (
            menu.add.range_slider(
                "Bottle Size :",
                range_values=(3, 7),
                padding=(24, 0, 0, 60),
                increment=1,
                font_color=GAME.COLOR3,
                default=GAME.bottle_size,
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
            menu.add.range_slider(
                "Colors :",
                range_values=(2, 6),
                padding=(24, 0, 0, 60),
                increment=1,
                font_color=GAME.COLOR3,
                default=GAME.colors,
                range_line_height=3,
                range_text_value_color=GAME.COLORS["BLACK"],
                slider_color=GAME.COLORS["BLACK"],
                slider_selected_color=GAME.COLORS["BLACK"],
                slider_text_value_bgcolor=GAME.COLOR2,
                slider_text_value_color=GAME.COLORS["WHITE"],
                range_line_color=GAME.COLORS["BLACK"],
                range_text_value_tick_color=GAME.COLORS["BLACK"],
                range_text_value_tick_thick=3,
                onchange=lambda i: set_game_parameters(i, 3),
                value_format=lambda x: str(int(x)),
            )
        )
    )
    for widget in GAME.widgets:
        frame2.pack(widget)

    # bottom "frame"
    _b = menu.add.button(
        " PLAY ",
        font_color=(38, 158, 151),
        action=start_game,
        font_size=60,
        align=pygame_menu.locals.ALIGN_CENTER,
    )

    _b.set_background_color(color=(4, 47, 58))
    _b._font_selected_color = GAME.COLORS["WHITE"]

    return menu
