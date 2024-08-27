import math
import time
from datetime import datetime as dt, timedelta as td
import pygame
from pygame.locals import *


class Display:

    def __init__(self, ENV, ATC):
        self.ENV = ENV
        self.ATC = ATC

    def render_table(self, surface, table_data, width, height):
        left_margin = 30
        top_margin = 50
        rows = len(table_data)
        cols = len(table_data[0])
        cell_width = (width - left_margin * 2) // cols
        cell_height = (height - top_margin * 2) // rows
        for row, row_data in enumerate(table_data):
            for col, col_data in enumerate(row_data):
                table = pygame.Surface((cell_width, cell_height))
                table.fill(self.ENV.BLACK)
                self.render_text(
                    surface=table,
                    font=self.ENV.FONT12,
                    text=[(col_data)],
                    fgColor=self.ENV.WHITE,
                )
                surface.blit(
                    source=table,
                    dest=(
                        cell_width * col + left_margin,
                        cell_height * row + top_margin,
                    ),
                )

    def render_text(self, surface, font, text, fgColor, x0=0, y0=0, dy=0):
        for deltay, line in enumerate(text):
            _t = font.render(line[0], True, fgColor, line[1])
            surface.blit(source=_t, dest=(x0, y0 + deltay * dy))

    def update_pygame_display(self):
        # load all level-2 background surfaces to reset screen
        for surfaces in self.ATC.allLevel2Surfaces:
            surfaces[0].blit(source=surfaces[1], dest=(0, 0))
        # ILS projection lines (toggle)
        if self.ENV.guidelineActive:
            for runway in self.ATC.airspaceInfo["runways"]:
                for head in ("headL", "headR"):
                    _x = runway[head]["x"] - (
                        math.cos(math.radians(runway[head]["heading"] - 90)) * 1000
                    )
                    _y = runway[head]["y"] - (
                        math.sin(math.radians(runway[head]["heading"] - 90)) * 1000
                    )
                    pygame.draw.line(
                        self.ATC.radarSurface,
                        self.ENV.GRAY,
                        (runway[head]["x"], runway[head]["y"]),
                        (_x, _y),
                        width=runway["width"],
                    )

        # load Radar main surface + Inventory main surface
        for entity in self.ATC.activeAirplanes:
            if entity.onRadar:
                self.ATC.radarSurface.blit(
                    source=entity.boxSurface, dest=entity.boxPosition
                )
                pygame.draw.line(
                    self.ATC.radarSurface,
                    self.ENV.RED if entity.isInbound else self.ENV.WHITE,
                    entity.tailPosition0,
                    entity.tailPosition1,
                )
                if self.ENV.tagActive:
                    self.ATC.radarSurface.blit(
                        source=entity.tagText0, dest=entity.tagPosition0
                    )
                    self.ATC.radarSurface.blit(
                        source=entity.tagText1, dest=entity.tagPosition1
                    )
            if entity.isInbound:
                self.ATC.inventoryArrivalsSurface.blit(
                    source=entity.inventoryText, dest=entity.inventoryPosition
                )
            else:
                self.ATC.inventoryDeparturesSurface.blit(
                    source=entity.inventoryText, dest=entity.inventoryPosition
                )
        # load Message main surface
        self.render_text(
            surface=self.ATC.messageSurface,
            font=self.ENV.FONT12,
            text=[(i[0], i[2]) for i in self.ATC.messageText],
            fgColor=self.ENV.WHITE,
            x0=5,
            y0=4,
            dy=15,
        )
        # load Input Command main surface
        self.render_text(
            surface=self.ATC.inputSurface,
            font=self.ENV.FONT20,
            text=[(self.ATC.commandText, self.ENV.WHITE)],
            fgColor=self.ENV.BLACK,
            x0=5,
            y0=20,
        )
        # load Airpsace Data main surface
        _text = [
            (f"GMT: {dt.strftime(dt.now(),'%H:%M:%S')}", self.ENV.BG_CONTROLS),
            (
                f"Wind: {self.ENV.windSpeed} knots @ {self.ENV.windDirection:03}°.",
                self.ENV.BG_CONTROLS,
            ),
            (f"Simulation Time: {str(self.ENV.simTime)[:-7]}.", self.ENV.BG_CONTROLS),
            (f"Airspace Information:", self.ENV.BG_CONTROLS),
            (
                f"Ground Level: {self.ATC.airspaceInfo['altitudes']['groundLevel']} feet.",
                self.ENV.BG_CONTROLS,
            ),
            (
                f"Handoff Altitude: {self.ATC.airspaceInfo['altitudes']['handOff']} feet.",
                self.ENV.BG_CONTROLS,
            ),
            (
                f"Game Objective: {self.ENV.game_modes[self.ENV.game_mode].title()} - Category {self.ENV.game_mode_goal}",
                self.ENV.BG_CONTROLS,
            ),
        ]
        self.render_text(
            surface=self.ATC.weatherSurface,
            font=self.ENV.FONT14,
            text=_text,
            fgColor=self.ENV.BLACK,
            x0=10,
            y0=25,
            dy=30,
        )

        # load Console main surface
        self.ENV.score["total"] = round(
            (
                self.ENV.score["departures"]
                + self.ENV.score["arrivals"]
                + self.ENV.score["expediteCommands"]
                + self.ENV.score["uncontrolledExits"]
                + self.ENV.score["warnings"]
                + self.ENV.score["goArounds"]
            ),
            1,
        )
        text = [
            [(f"{j.title()}", self.ENV.BLACK), (f"{str(i)}", self.ENV.BLACK)]
            for i, j in zip(self.ENV.score.values(), self.ENV.SCORE_TITLES)
        ]

        self.render_table(
            surface=self.ATC.consoleSurface,
            table_data=text,
            width=self.ATC.CONTROLS_WIDTH,
            height=self.ATC.CONSOLE_HEIGHT,
        )
        # load all level-2 main surfaces
        for surfaces in self.ATC.allLevel2Surfaces:
            self.ATC.displaySurface.blit(source=surfaces[0], dest=surfaces[2])

        pygame.display.update()

    def pop_up(self, action, pause):
        # define text that goes in popup
        if action == "HELP":
            message = self.ENV.FONT12.render(
                "Help Text", True, self.ENV.BLACK, self.ENV.WHITE
            )
        elif action == "QUIT":
            message = self.ENV.FONT12.render(
                "ENTER to quit. Any other key to continue.",
                True,
                self.ENV.BLACK,
                self.ENV.WHITE,
            )
        elif action == "TOGGLE":
            message = self.ENV.FONT20.render(
                "TOGGLE", True, self.ENV.BLACK, self.ENV.WHITE
            )
        # create popup and display
        popupSizex, popupSizey = 500, 100
        popUpSurface = pygame.Surface((popupSizex, popupSizey))
        popUpSurface.fill(self.ENV.WHITE)
        title = self.ENV.FONT20.render(
            "GAME PAUSED", True, self.ENV.RED, self.ENV.WHITE
        )
        popUpSurface.blit(
            source=title, dest=((popupSizex - title.get_width()) // 2, 10)
        )
        popUpSurface.blit(
            source=message, dest=((popupSizex - message.get_width()) // 2, 50)
        )
        self.ATC.displaySurface.blit(
            source=popUpSurface,
            dest=(
                self.ENV.DISPLAY_WIDTH // 2 - 250,
                self.ENV.DISPLAY_HEIGHT // 2 - 100,
            ),
        )
        pygame.display.update()
        # take action when user presses key
        if pause > 0:
            time.sleep(pause)
            return
        else:
            while True:
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        if event.key == 13 and action == "QUIT":
                            quit()
                        elif event.key == 27:
                            self.ENV.simTimeSplit = dt.now()
                            return
