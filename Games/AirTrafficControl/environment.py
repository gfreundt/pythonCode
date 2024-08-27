import json
import os
from datetime import datetime as dt, timedelta as td
import random
import pygame
from pygame.locals import *
import sqlite3


class Environment:

    def __init__(self, args):

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (171, 35, 40)
        self.GREEN = (0, 110, 51)
        self.BROWN = (102, 51, 0)
        self.BLUE = (0, 0, 153)
        self.LIGHT_BLUE = (51, 153, 255)
        self.GRAY = (120, 120, 120)
        self.BG = (25, 72, 80)
        self.BG_CONTROLS = self.WHITE  # (0, 102, 102)
        self.INV_COLORS = [(44, 93, 118), (74, 148, 186)]
        self.RESOURCES_PATH = os.path.join(
            os.getcwd()[:2], r"\pythonCode", "Resources", "Fonts"
        )

        self.DISPLAY_WIDTH = pygame.display.Info().current_w
        self.DISPLAY_HEIGHT = pygame.display.Info().current_h // 1.01
        self.FONT9 = pygame.font.Font(
            os.path.join(self.RESOURCES_PATH, "seguisym.ttf"), 9
        )
        self.FONT12 = pygame.font.Font(
            os.path.join(self.RESOURCES_PATH, "seguisym.ttf"), 12
        )
        self.FONT14 = pygame.font.Font(
            os.path.join(self.RESOURCES_PATH, "seguisym.ttf"), 14
        )
        self.FONT20 = pygame.font.Font(
            os.path.join(self.RESOURCES_PATH, "roboto.ttf"), 20
        )
        self.SCALE = 90
        self.SPEED = 1
        self.FPS = 60
        self.NUMPAD_KEYS = {
            K_KP0: "0",
            K_KP1: "1",
            K_KP2: "2",
            K_KP3: "3",
            K_KP4: "4",
            K_KP5: "5",
            K_KP6: "6",
            K_KP7: "7",
            K_KP8: "8",
            K_KP9: "9",
        }
        self.FUNCTION_KEYS = {
            K_F1: "F1",
            K_F2: "F2",
            K_F3: "F3",
            K_F4: "F4",
            K_F5: "F5",
            K_F6: "F6",
            K_F7: "F7",
            K_F8: "F8",
            K_F9: "F9",
            K_F10: "F10",
            K_F11: "F11",
            K_F12: "F12",
        }

        self.MAX_AIRPLANES = 10

        SQLDATABASE = os.path.join(os.getcwd(), "highscores.db")
        self.conn = sqlite3.connect(SQLDATABASE)
        self.cursor = self.conn.cursor()

        self.cursor.execute("select DISTINCT Mode from Levels")
        self.game_modes = [i[0] for i in self.cursor.fetchall()]

        self.player_name = "Gabriel"  # Temporary

        with open("atc-airplanes.json", mode="r") as json_file:
            self.airplaneData = json.loads(json_file.read())
        with open("atc-airspace.json", mode="r") as json_file:
            self.airspaceData = json.loads(json_file.read())

        self.MESSAGE_DISPLAY_TIME = 20  # seconds
        self.ILS_ANGLE = 60  # degrees
        self.ILS_HEADING = 60  # degrees
        self.MIN_V_SEPARATION = 1000
        self.MIN_H_SEPARATION = 60
        self.CHANCE_EMERGENCY = 0.01
        self.CHANCE_MISSED_APPROACH = 0.03
        self.ARRIVALS_RATIO = 50
        self.DELAY_NEXT_PLANE = td(seconds=10)
        self.PENALTY_LIFETIME = td(minutes=15)
        self.PRESET_DEPART_ALTITUDE_TARGET = 20000
        self.game_over = False

        self.ERRORS = [
            "*VOID*",
            "Last Command not Understood",
            "Unable to Comply",
            "Flight Number not Available",
        ]
        self.collision = False
        self.audioOn = False
        self.SCORE_TITLES = [
            "Controlled Departures (+)",
            "Controlled Arrivals (+)",
            "Expedite Commands (-)",
            "Uncontrolled Exits (-)",
            "Warnings (-)",
            "Go Arounds (-)",
            "Total Score",
            "Avg Time Departures",
            "Avg Time Arrivals",
        ]
        self.score = {
            "departures": 0,
            "arrivals": 0,
            "expediteCommands": 0.0,
            "uncontrolledExits": 0,
            "warnings": 0.0,
            "goArounds": 0,
            "total": 0,
            "departuresAvgTime": td(seconds=0),
            "arrivalsAvgTime": td(seconds=0),
        }
        self.simTime = dt.now() - dt.now()
        self.simTimeSplit = dt.now()
        self.lastPlaneInit = self.simTime
        self.departuresTotTime = td(seconds=0)
        self.arrivalsTotTime = td(seconds=0)

        # random wind speed and direction
        self.windSpeed = random.randint(0, 30)
        self.windDirection = random.randint(0, 360)

        # general display variables
        self.tagActive = True
        self.tagDeltaOptions = [(15, 15), (-45, 15), (-45, -40), (15, -40)]
        self.tagDeltaSelected = 0
        self.guidelineActive = False

        # check for default overrides at command line
        if "-D" in args:
            self.ARRIVALS_RATIO = 0
        if "-A" in args:
            self.ARRIVALS_RATIO = 100
        if "-M" in args:
            self.MAX_AIRPLANES = int(args[args.index("-M") + 1])
        if "-S" in args:
            self.GAME_MODE = int(args[args.index("-S") + 1])
