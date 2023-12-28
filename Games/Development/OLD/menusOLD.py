import json
import pygame_menu


def menu(GAME):
    def set_game_parameters(value, parameter):
        val = int(value)
        GAME.parameters[parameter] = val

    def start_game():
        GAME.stage = 1

    def press_preset_level():
        GAME.parameters = LEVEL_PRESETS[int(menu.get_selected_widget()._id)]
        # update widgets
        for k, widget in enumerate(widgets):
            if hasattr(widget, "_value"):
                widgets[k]._value = [GAME.parameters[k], 0]
            else:
                widgets[k]._state = GAME.parameters[k]

    with open("game_parameters.json", mode="r") as file:
        init_values = json.load(file)[GAME.game]

    GAME.parameters = list(init_values["LEVEL_PRESETS"][0])
    LEVEL_PRESETS = init_values["LEVEL_PRESETS"]
    MENU_WIDTH, MENU_HEIGHT = init_values["MENU_WIDTH"], init_values["MENU_HEIGHT"]
    GAME_TITLE = init_values["GAME_TITLE"]
    WIDGETS = init_values["WIDGETS"]

    MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
    MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
    MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()
    MENU_THEME.selection_color = GAME.PALETTE[2]
    # MENU_THEME.widget_font = pygame_menu.font.FONT_FIRACODE

    menu = pygame_menu.Menu(
        GAME_TITLE,
        MENU_WIDTH,
        MENU_HEIGHT,
        theme=MENU_THEME,
        center_content=True,
        onclose=pygame_menu.events.CLOSE,
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
            button_id=str(level),
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
                onchange=lambda i: set_game_parameters(i, k),
                default=GAME.parameters[k],
                value_format=lambda x: str(int(x)),
            )
        elif w["type"] == "switch":
            _widget = menu.add.toggle_switch(
                w["name"],
                padding=(24, 0, 0, w["padding"]),
                font_color=GAME.PALETTE[2],
                state_color=(GAME.PALETTE[2], (255, 255, 255)),
                state_text_font_color=((255, 255, 255), GAME.PALETTE[2]),
                state_text=("No", "Yes"),
                onchange=lambda i: set_game_parameters(i, k),
                default=GAME.parameters[k],
                width=70,
                slider_thickness=0,
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
