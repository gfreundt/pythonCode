import math
import sys
import pygame
from pygame.locals import *
from gtts import gTTS

import environment, display, airspace, userinput


pygame.init()


# TODO: help
# TODO: intro menu to select airspace and level
# TODO: pop-up changes height depending on content
# TODO: penalty for too much time aircraft life

# TODO: multi-command line
# TODO: priority departure


def init_load_console():
    # add Controls - Message background
    ATC.messageSurface = pygame.Surface((ATC.CONTROLS_WIDTH, ATC.MESSAGE_HEIGHT - 2))
    ATC.messageBG = pygame.Surface.copy(ATC.messageSurface)
    ATC.messageSurface.fill((ATC.ENV.BLACK))
    ATC.messageText = []

    # add Controls - Inventory background, split columns for Arrivals and Departures
    ATC.inventoryArrivalsSurface = pygame.Surface(
        (ATC.CONTROLS_WIDTH // 2, ATC.INVENTORY_HEIGHT - 2)
    )
    ATC.inventoryArrivalsSurface.fill(ATC.ENV.BLACK)
    DISP.render_text(
        surface=ATC.inventoryArrivalsSurface,
        font=ATC.ENV.FONT20,
        text=[("ARRIVALS", ATC.ENV.BLACK)],
        fgColor=ATC.ENV.WHITE,
        x0=115,
        y0=10,
        dy=0,
    )

    ATC.inventoryArrivalsBG = pygame.Surface.copy(ATC.inventoryArrivalsSurface)

    ATC.inventoryDeparturesSurface = pygame.Surface(
        (ATC.CONTROLS_WIDTH // 2, ATC.INVENTORY_HEIGHT - 2)
    )
    ATC.inventoryDeparturesSurface.fill(ATC.ENV.BLACK)
    DISP.render_text(
        surface=ATC.inventoryDeparturesSurface,
        font=ATC.ENV.FONT20,
        text=[("DEPARTURES", ATC.ENV.BLACK)],
        fgColor=ATC.ENV.WHITE,
        x0=105,
        y0=10,
    )
    ATC.inventoryDeparturesBG = pygame.Surface.copy(ATC.inventoryDeparturesSurface)

    # add Controls - Input Command background
    ATC.inputSurface = pygame.Surface((ATC.CONTROLS_WIDTH, ATC.INVENTORY_HEIGHT - 2))
    ATC.inputSurface.fill((ATC.ENV.WHITE))
    ATC.inputBG = pygame.Surface.copy(ATC.inputSurface)
    DISP.render_text(
        surface=ATC.inputBG,
        font=ATC.ENV.FONT9,
        text=[("Enter New Command", ATC.ENV.WHITE)],
        fgColor=ATC.ENV.BLACK,
        x0=2,
        y0=2,
    )
    ATC.commandText = ""

    # add Controls - Console background
    ATC.consoleSurface = pygame.Surface((ATC.CONTROLS_WIDTH, ATC.CONSOLE_HEIGHT - 2))
    ATC.consoleSurface.fill((ATC.ENV.BLACK))
    ATC.consoleBG = pygame.Surface.copy(ATC.consoleSurface)
    DISP.render_text(
        surface=ATC.consoleBG,
        font=ATC.ENV.FONT20,
        text=[("SCORE", ATC.ENV.BLACK)],
        fgColor=ATC.ENV.WHITE,
        x0=145,
        y0=10,
    )

    # add Controls - Weather background
    ATC.weatherSurface = pygame.Surface((ATC.CONTROLS_WIDTH, ATC.WEATHER_HEIGHT - 2))
    ATC.weatherSurface.fill((ATC.ENV.BG_CONTROLS))
    ATC.weatherBG = pygame.Surface.copy(ATC.weatherSurface)
    img = pygame.transform.scale(
        pygame.image.load("atc_compass.png"),
        (ATC.WEATHER_HEIGHT, ATC.WEATHER_HEIGHT),
    )
    ATC.weatherBG.blit(source=img, dest=(ATC.CONTROLS_WIDTH // 2, 0))
    if ATC.ENV.windDirection < 90:
        dx, dy = (
            math.cos(math.radians(90 - ATC.ENV.windDirection)) * 41,
            math.sin(math.radians(90 - ATC.ENV.windDirection)) * -41,
        )
    elif ATC.ENV.windDirection < 180:
        dx, dy = (
            math.cos(math.radians(ATC.ENV.windDirection - 90)) * 41,
            math.sin(math.radians(ATC.ENV.windDirection - 90)) * 41,
        )
    elif ATC.ENV.windDirection < 270:
        dx, dy = (
            math.cos(math.radians(270 - ATC.ENV.windDirection)) * -41,
            math.sin(math.radians(270 - ATC.ENV.windDirection)) * 41,
        )
    else:
        dx, dy = (
            math.cos(math.radians(ATC.ENV.windDirection - 270)) * -41,
            math.sin(math.radians(ATC.ENV.windDirection - 270)) * -41,
        )
    center = (
        ATC.CONTROLS_WIDTH // 2 + ATC.WEATHER_HEIGHT // 2 + 1 + dx,
        ATC.WEATHER_HEIGHT // 2 + 4 + dy,
    )
    pygame.draw.circle(ATC.weatherBG, ATC.ENV.GREEN, center, 4, 4)

    ATC.allLevel2Surfaces = [
        [ATC.radarSurface, ATC.radarBG, (0, 0)],
        [ATC.messageSurface, ATC.messageBG, (ATC.RADAR_WIDTH + 5, 0)],
        [
            ATC.inventoryArrivalsSurface,
            ATC.inventoryArrivalsBG,
            (ATC.RADAR_WIDTH + 5, ATC.MESSAGE_HEIGHT + 2),
        ],
        [
            ATC.inventoryDeparturesSurface,
            ATC.inventoryDeparturesBG,
            (ATC.RADAR_WIDTH + ATC.CONTROLS_WIDTH // 2, ATC.MESSAGE_HEIGHT + 2),
        ],
        [
            ATC.inputSurface,
            ATC.inputBG,
            (ATC.RADAR_WIDTH + 5, ATC.MESSAGE_HEIGHT + ATC.INVENTORY_HEIGHT + 2),
        ],
        [
            ATC.consoleSurface,
            ATC.consoleBG,
            (
                ATC.RADAR_WIDTH + 5,
                ATC.MESSAGE_HEIGHT + ATC.INVENTORY_HEIGHT + ATC.INPUT_HEIGHT + 2,
            ),
        ],
        [
            ATC.weatherSurface,
            ATC.weatherBG,
            (
                ATC.RADAR_WIDTH + 5,
                ATC.MESSAGE_HEIGHT
                + ATC.INVENTORY_HEIGHT
                + ATC.INPUT_HEIGHT
                + ATC.CONSOLE_HEIGHT
                + 2,
            ),
        ],
    ]


def main():
    ATC.init_load_airspace()
    init_load_console()
    clock = pygame.time.Clock()
    delay = ENV.FPS // ENV.SPEED
    while True:
        clock.tick(ENV.FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                USER.process_keydown(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                USER.process_click(pos=pygame.mouse.get_pos())
        DISP.update_pygame_display()
        # actions happen with regulated frequency
        delay -= 1
        if delay == 0:
            ATC.next_frame()
            ATC.next_plane()
            delay = ENV.FPS // ENV.SPEED


ENV = environment.Environment(sys.argv)
ATC = airspace.Airspace(ENV=ENV)
DISP = display.Display(ENV=ENV, ATC=ATC)
USER = userinput.UserInput(ENV=ENV, ATC=ATC, DISP=DISP)

main()
