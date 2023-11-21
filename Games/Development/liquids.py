import pygame

from pygame.locals import *
import pygame_menu
import random
import os

pygame.init()


class Game:
    WORKING_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Games", "Development")
    RESOURCES_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources")
    FONT20 = pygame.font.Font(os.path.join(RESOURCES_PATH, "Fonts", "roboto.ttf"), 20)
    BOTTLE_IMAGE = pygame.transform.scale(
        pygame.image.load(os.path.join(WORKING_PATH, "empty-bottle.png")), (128, 128)
    )
    BACKGROUND_COLOR = (128, 128, 128)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    COLORS = {
        "R": (255, 0, 0),
        "B": (0, 0, 255),
        "G": (0, 255, 0),
        "Y": (225, 255, 0),
        "M": (106, 84, 12),
        " ": (255, 255, 255),
    }
    MAIN_SURFACE = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    LEVEL_PRESETS = [(12, 3, 4, 2), (20, 2, 5, 3), (38, 2, 6, 4), (50, 1, 6, 5)]

    full_bottles = 34
    empty_bottles = 1
    bottle_size = 4
    colors = 4  # range 2-6
    selected_bottle = False
    fr = -1
    moves_counter = 0


def update_display():
    GAME.MAIN_SURFACE.fill(GAME.BACKGROUND_COLOR)
    for row in range(len(GAME.collection) // 10 + 1):
        for col in range(min(10, len(GAME.collection) - 10 * row)):
            GAME.MAIN_SURFACE.blit(
                source=GAME.surfaces[row * 10 + col],
                dest=(100 + 100 * col, 100 + 200 * row),
            )
            text = GAME.FONT20.render(
                f"{row*10+col:02d}",
                True,
                GAME.RED if GAME.fr == (10 * row + col) else GAME.BLACK,
                GAME.BACKGROUND_COLOR,
            )
            GAME.MAIN_SURFACE.blit(source=text, dest=(155 + 100 * col, 230 + 200 * row))
    pygame.display.flip()


def main_menu():
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

    def press_preset_level(level):
        print(level)
        (
            GAME.full_bottles,
            GAME.empty_bottles,
            GAME.bottle_size,
            GAME.colors,
        ) = GAME.LEVEL_PRESETS[level]
        GAME.stage = 1

    MENU_THEME = pygame_menu.themes.THEME_SOLARIZED.copy()
    MENU_THEME.title_bar_style = pygame_menu.widgets.MENUBAR_STYLE_ADAPTIVE
    MENU_THEME.widget_selection_effect = pygame_menu.widgets.SimpleSelection()

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
        height=100, width=500, align=pygame_menu.locals.ALIGN_CENTER
    )
    frame1.set_title(" Preset Options")
    button_selection = (
        pygame_menu.widgets.SimpleSelection()
        .set_background_color(GAME.BLACK)
        .set_color(GAME.BLUE)
    )
    for level, text in enumerate(("Easy", "Medium", "Hard", "Expert")):
        b = menu.add.button(
            text,
            action=lambda: press_preset_level(level),
            padding=(5, 18),
            align=pygame_menu.locals.ALIGN_CENTER,
        )

        b.set_selection_effect(button_selection)
        frame1.pack(b)

    # define middle frame
    frame2 = menu.add.frame_v(height=300, width=500)
    frame2.set_title(" Manual Options")
    frame2.pack(
        menu.add.range_slider(
            f"{'Colors :':>26}",
            range_values=[i for i in range(2, 6)],
            onchange=lambda i: set_game_parameters(i, 3),
            default=GAME.colors,
            slider_text_value_enabled=False,
        )
    )
    frame2.pack(
        menu.add.range_slider(
            f"{'Full Bottles :':>24}",
            range_values=(8, 50),
            increment=1,
            default=GAME.full_bottles,
            onchange=lambda i: set_game_parameters(i, 0),
            value_format=lambda x: str(int(x)),
        )
    )
    frame2.pack(
        menu.add.range_slider(
            f"{'Empty Bottles :':>20}",
            range_values=[i for i in range(1, 4)],
            onchange=lambda i: set_game_parameters(i, 1),
            default=GAME.empty_bottles,
            slider_text_value_enabled=False,
        )
    )
    frame2.pack(
        menu.add.range_slider(
            f"{'Bottle Size :':>24}",
            range_values=[i for i in range(3, 7)],
            onchange=lambda i: set_game_parameters(i, 2),
            default=GAME.bottle_size,
            slider_text_value_enabled=False,
        )
    )

    frame3 = menu.add.frame_h(height=100, width=500)
    frame3.pack(
        menu.add.button("Play", action=start_game, padding=(5, 60), font_size=60)
    )
    frame3.pack(
        menu.add.button(
            "Quit", action=pygame_menu.events.EXIT, padding=(5, 60), font_size=60
        )
    )

    return menu


def setup():
    with_liquid = "".join(
        [
            i * ((GAME.full_bottles // GAME.colors) * GAME.bottle_size)
            for i in list(GAME.COLORS.keys())[: GAME.colors]
        ]
    )
    allAvailable = list(
        with_liquid + " " * (GAME.full_bottles * GAME.bottle_size - len(with_liquid))
    )
    random.shuffle(allAvailable)
    allAvailable += list([" "] * GAME.bottle_size * GAME.empty_bottles)
    GAME.collection = [
        allAvailable[i * GAME.bottle_size : (i + 1) * GAME.bottle_size]
        for i in range(GAME.full_bottles + GAME.empty_bottles)
    ]
    # spaces must be on top (fix later)
    for k, bottle in enumerate(GAME.collection):
        if " " in bottle:
            GAME.collection[k] = sorted(GAME.collection[k], reverse=False)
    # create initial pygame entities
    GAME.surfaces = [
        update_entity(GAME.BOTTLE_IMAGE.copy(), bottle) for bottle in GAME.collection
    ]


def process_click(pos, button):
    bottle = get_selected_bottle(pos)
    if bottle > -1:
        if GAME.selected_bottle:
            transfer(GAME.fr, to=bottle)
            GAME.selected_bottle = False
            GAME.fr = -1
        else:
            GAME.fr = bottle
            GAME.selected_bottle = True


def get_selected_bottle(pos):
    for k, bottle in enumerate(GAME.surfaces):
        if bottle.get_rect(
            topleft=(100 + 100 * (k % 10), 100 + 200 * (k // 10))
        ).collidepoint(pos):
            return k
    return -1


def transfer(fr, to):
    # capture errors
    if fr >= len(GAME.collection) or to >= len(GAME.collection):
        print("Bottle out of range")
        return True
    if fr == to:
        print("Must be different bottles")
        return True
    if GAME.collection[fr].count(" ") == len(GAME.collection[0]):
        print("Error: nothing in FROM bottle")
        return True
    elif GAME.collection[to].count(" ") == 0:
        print("Error: TO bottle is full")
        return True

    # move content from bottle to bottle
    bottle_from, bottle_to = GAME.collection[fr], GAME.collection[to]
    pos_from = 0
    for k, c in enumerate(bottle_from):
        if c == " ":
            pos_from = k + 1
    for k, c in enumerate(bottle_to):
        if c == " ":
            pos_to = k
    bottle_to[pos_to] = bottle_from[pos_from]
    bottle_from[pos_from] = " "

    # update pygame entities
    GAME.surfaces[fr] = update_entity(GAME.surfaces[fr], bottle_from)
    GAME.surfaces[to] = update_entity(GAME.surfaces[to], bottle_to)

    # update other game variables
    GAME.moves_counter += 1


def update_entity(surface, content):
    height = 90 // GAME.bottle_size
    for y0, color in enumerate(content):
        pygame.draw.rect(
            surface, GAME.COLORS[color], (36, 30 + y0 * height, 56, height)
        )
    return surface


def check_end():
    for bottle in GAME.collection:
        if bottle.count(bottle[0]) < GAME.bottle_size:
            return False
    return True


def main():
    mainmenu = main_menu()
    GAME.stage = 0

    while mainmenu.is_enabled():
        if GAME.stage == 0:
            mainmenu.mainloop(GAME.MAIN_SURFACE, disable_loop=True)
            # print(GAME.full_bottles, GAME.empty_bottles, GAME.bottle_size, GAME.colors)
        elif GAME.stage == 1:
            setup()
            GAME.stage = 2
        elif GAME.stage == 2:
            events = pygame.event.get()
            for event in events:
                if event.type == QUIT or event.type == KEYDOWN:
                    # pygame.quit()
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    process_click(pos=pygame.mouse.get_pos(), button=event.button)
                update_display()

                if check_end():
                    print(f"Finished Successfully in {GAME.moves_counter} moves!")
                    return


GAME = Game()


main()
