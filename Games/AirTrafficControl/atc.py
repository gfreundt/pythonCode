import math
import random
import json, os, sys, time
from datetime import datetime as dt
from datetime import timedelta as td
import pygame
from pygame.locals import *
from gtts import gTTS


pygame.init()


# TODO: help
# TODO: intro menu to select airspace and level
# TODO: pop-up changes height depending on content
# TODO: penalty for too much time aircraft life

# TODO: multi-command line
# TODO: priority departure


class Environment:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (171, 35, 40)
    GREEN = (0, 110, 51)
    BROWN = (102, 51, 0)
    BLUE = (0, 0, 153)
    LIGHT_BLUE = (51, 153, 255)
    GRAY = (120, 120, 120)
    BG = (25, 72, 80)
    BG_CONTROLS = (0, 102, 102)
    INV_COLORS = [(44, 93, 118), (74, 148, 186)]
    RESOURCES_PATH = os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Fonts")

    DISPLAY_WIDTH = pygame.display.Info().current_w
    DISPLAY_HEIGHT = pygame.display.Info().current_h // 1.01
    FONT9 = pygame.font.Font(os.path.join(RESOURCES_PATH, "seguisym.ttf"), 9)
    FONT12 = pygame.font.Font(os.path.join(RESOURCES_PATH, "seguisym.ttf"), 12)
    FONT14 = pygame.font.Font(os.path.join(RESOURCES_PATH, "seguisym.ttf"), 14)
    FONT20 = pygame.font.Font(os.path.join(RESOURCES_PATH, "roboto.ttf"), 20)
    SCALE = 90
    SPEED = 1
    FPS = 60
    NUMPAD_KEYS = {
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
    FUNCTION_KEYS = {
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

    MAX_AIRPLANES = 10
    with open("atc-airplanes.json", mode="r") as json_file:
        airplaneData = json.loads(json_file.read())
    MESSAGE_DISPLAY_TIME = 20  # seconds
    ILS_ANGLE = 60  # degrees
    ILS_HEADING = 60  # degrees
    MIN_V_SEPARATION = 1000
    MIN_H_SEPARATION = 60
    EMERGENCY_CHANCE = 1
    ARRIVALS_RATIO = 50
    DELAY_NEXT_PLANE = td(seconds=10)
    PENALTY_LIFETIME = td(minutes=15)

    ERRORS = [
        "*VOID*",
        "Last Command not Understood",
        "Unable to Comply",
        "Flight Number not Available",
    ]
    collision = False
    audioOn = False
    SCORE_TITLES = [
        "Controlled Departures (+)",
        "Controlled Arrivals (+)",
        "Expedite Commands (-)",
        "Uncontrolled Exits (-)",
        "Warnings (-)",
        "Go Arounds (-)",
        "Total Score",
    ]
    score = {
        "departures": 0,
        "arrivals": 0,
        "expediteCommands": 0.0,
        "uncontrolledExits": 0,
        "warnings": 0.0,
        "goArounds": 0,
        "total": 0,
    }
    simTime = dt.now() - dt.now()
    simTimeSplit = dt.now()
    lastPlaneInit = simTime

    # random wind speed and direction
    windSpeed = random.randint(0, 30)
    windDirection = random.randint(0, 360)

    # general display variables
    tagActive = True
    guidelineActive = False

    def __init__(self, args):
        # check for default overrides at command line
        if "-D" in args:
            self.ARRIVALS_RATIO = 0
        if "-A" in args:
            self.ARRIVALS_RATIO = 100
        if "-M" in args:
            self.MAX_AIRPLANES = int(args[args.index("-M") + 1])


class Airspace:
    def __init__(self, *args) -> None:
        # load plane tech spec data from json file
        self.activeAirplanes = []
        self.lastCallSign = ""
        self.init_pygame()
        self.init_load_airspace()
        self.init_load_console()

    def init_pygame(self):
        # pygame init
        os.environ["SDL_VIDEO_WINDOW_POS"] = "1, 1"
        self.displaySurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.RADAR_WIDTH = int(ENV.DISPLAY_WIDTH * 0.75)
        self.RADAR_HEIGHT = ENV.DISPLAY_HEIGHT
        self.CONTROLS_WIDTH = int(ENV.DISPLAY_WIDTH * 0.25)
        self.MESSAGE_HEIGHT = int(ENV.DISPLAY_HEIGHT * 0.1)
        self.INVENTORY_HEIGHT = int(ENV.DISPLAY_HEIGHT * 0.45)
        self.INPUT_HEIGHT = int(ENV.DISPLAY_HEIGHT * 0.05)
        self.CONSOLE_HEIGHT = int(ENV.DISPLAY_HEIGHT * 0.2)
        self.WEATHER_HEIGHT = int(ENV.DISPLAY_HEIGHT * 0.2)

        pygame.display.set_caption("ATC Simulator")

    def init_load_airspace(self):
        with open("atc-airspace.json", mode="r") as json_file:
            self.airspaceInfo = json.loads(json_file.read())
        # create VOR shape entities
        triangle = pygame.Surface((10, 10))
        triangle.fill(ENV.BG)
        pygame.draw.polygon(triangle, ENV.WHITE, ((5, 0), (0, 9), (9, 9)), True)
        circles = pygame.Surface((10, 10))
        circles.fill(ENV.BG)
        pygame.draw.circle(circles, ENV.WHITE, (5, 5), 5, True)
        pygame.draw.circle(circles, ENV.WHITE, (5, 5), 3, True)
        star = pygame.Surface((10, 10))
        star.fill(ENV.BG)
        _s = ((5, 1), (7, 4), (9, 5), (7, 6), (5, 9), (3, 6), (1, 5), (3, 4), (5, 1))
        pygame.draw.polygon(star, ENV.WHITE, _s, True)
        symbols = {"TRIANGLE": triangle, "CIRCLES": circles, "STAR": star}

        # create Radar main and background surfaces
        self.radarSurface = pygame.Surface((ENV.DISPLAY_WIDTH, ENV.DISPLAY_HEIGHT))
        self.radarSurface.fill(ENV.BG)
        self.radarBG = pygame.Surface.copy(self.radarSurface)
        # add VOR entities to Radar background surface
        for vor in self.airspaceInfo["VOR"]:
            self.radarBG.blit(
                source=symbols[vor["symbol"]], dest=((vor["x"], vor["y"]))
            )
            self.radarBG.blit(
                source=ENV.FONT14.render(
                    vor["name"],
                    True,
                    ENV.WHITE,
                    ENV.BG,
                ),
                dest=(vor["x"] + 14, vor["y"] - 3),
            )
        # add Runway entities to Radar background surface
        for runway in self.airspaceInfo["runways"]:
            pygame.draw.line(
                self.radarBG,
                ENV.WHITE,
                (runway["headL"]["x"], runway["headL"]["y"]),
                (runway["headR"]["x"], runway["headR"]["y"]),
                width=runway["width"],
            )
            for d in ("headL", "headR"):
                self.radarBG.blit(
                    source=ENV.FONT14.render(
                        runway[d]["tag"]["text"], True, ENV.WHITE, ENV.BG
                    ),
                    dest=runway[d]["tag"]["xy"],
                )

    def init_load_console(self):
        # add Controls - Message background
        self.messageSurface = pygame.Surface(
            (self.CONTROLS_WIDTH, self.MESSAGE_HEIGHT - 2)
        )
        self.messageBG = pygame.Surface.copy(self.messageSurface)
        self.messageSurface.fill((ENV.BLACK))
        self.messageText = []

        # add Controls - Inventory background, split columns for Arrivals and Departures
        self.inventoryArrivalsSurface = pygame.Surface(
            (self.CONTROLS_WIDTH // 2, self.INVENTORY_HEIGHT - 2)
        )
        self.inventoryArrivalsSurface.fill(ENV.BLACK)
        render_text(
            surface=self.inventoryArrivalsSurface,
            font=ENV.FONT20,
            text=[("ARRIVALS", ENV.BLACK)],
            fgColor=ENV.WHITE,
            x0=115,
            y0=10,
            dy=0,
        )

        self.inventoryArrivalsBG = pygame.Surface.copy(self.inventoryArrivalsSurface)

        self.inventoryDeparturesSurface = pygame.Surface(
            (self.CONTROLS_WIDTH // 2, self.INVENTORY_HEIGHT - 2)
        )
        self.inventoryDeparturesSurface.fill(ENV.BLACK)
        render_text(
            surface=self.inventoryDeparturesSurface,
            font=ENV.FONT20,
            text=[("DEPARTURES", ENV.BLACK)],
            fgColor=ENV.WHITE,
            x0=105,
            y0=10,
        )
        self.inventoryDeparturesBG = pygame.Surface.copy(
            self.inventoryDeparturesSurface
        )

        # add Controls - Input Command background
        self.inputSurface = pygame.Surface(
            (self.CONTROLS_WIDTH, self.INVENTORY_HEIGHT - 2)
        )
        self.inputSurface.fill((ENV.WHITE))
        self.inputBG = pygame.Surface.copy(self.inputSurface)
        render_text(
            surface=self.inputBG,
            font=ENV.FONT9,
            text=[("Enter New Command", ENV.WHITE)],
            fgColor=ENV.BLACK,
            x0=2,
            y0=2,
        )
        self.commandText = ""

        # add Controls - Console background
        self.consoleSurface = pygame.Surface(
            (self.CONTROLS_WIDTH, self.CONSOLE_HEIGHT - 2)
        )
        self.consoleSurface.fill((ENV.BLACK))
        self.consoleBG = pygame.Surface.copy(self.consoleSurface)
        render_text(
            surface=self.consoleBG,
            font=ENV.FONT20,
            text=[("SCORE", ENV.BLACK)],
            fgColor=ENV.WHITE,
            x0=145,
            y0=10,
        )

        # add Controls - Weather background
        self.weatherSurface = pygame.Surface(
            (self.CONTROLS_WIDTH, self.WEATHER_HEIGHT - 2)
        )
        self.weatherSurface.fill((ENV.BG_CONTROLS))
        self.weatherBG = pygame.Surface.copy(self.weatherSurface)
        img = pygame.transform.scale(
            pygame.image.load("atc_compass.png"),
            (self.WEATHER_HEIGHT, self.WEATHER_HEIGHT),
        )
        self.weatherBG.blit(source=img, dest=(self.CONTROLS_WIDTH // 2, 0))
        if ENV.windDirection < 90:
            dx, dy = (
                math.cos(math.radians(90 - ENV.windDirection)) * 41,
                math.sin(math.radians(90 - ENV.windDirection)) * -41,
            )
        elif ENV.windDirection < 180:
            dx, dy = (
                math.cos(math.radians(ENV.windDirection - 90)) * 41,
                math.sin(math.radians(ENV.windDirection - 90)) * 41,
            )
        elif ENV.windDirection < 270:
            dx, dy = (
                math.cos(math.radians(270 - ENV.windDirection)) * -41,
                math.sin(math.radians(270 - ENV.windDirection)) * 41,
            )
        else:
            dx, dy = (
                math.cos(math.radians(ENV.windDirection - 270)) * -41,
                math.sin(math.radians(ENV.windDirection - 270)) * -41,
            )
        center = (
            self.CONTROLS_WIDTH // 2 + self.WEATHER_HEIGHT // 2 + 1 + dx,
            self.WEATHER_HEIGHT // 2 + 4 + dy,
        )
        pygame.draw.circle(self.weatherBG, ENV.GREEN, center, 4, 4)

        self.allLevel2Surfaces = [
            [self.radarSurface, self.radarBG, (0, 0)],
            [self.messageSurface, self.messageBG, (self.RADAR_WIDTH + 5, 0)],
            [
                self.inventoryArrivalsSurface,
                self.inventoryArrivalsBG,
                (self.RADAR_WIDTH + 5, self.MESSAGE_HEIGHT + 2),
            ],
            [
                self.inventoryDeparturesSurface,
                self.inventoryDeparturesBG,
                (self.RADAR_WIDTH + self.CONTROLS_WIDTH // 2, self.MESSAGE_HEIGHT + 2),
            ],
            [
                self.inputSurface,
                self.inputBG,
                (self.RADAR_WIDTH + 5, self.MESSAGE_HEIGHT + self.INVENTORY_HEIGHT + 2),
            ],
            [
                self.consoleSurface,
                self.consoleBG,
                (
                    self.RADAR_WIDTH + 5,
                    self.MESSAGE_HEIGHT + self.INVENTORY_HEIGHT + self.INPUT_HEIGHT + 2,
                ),
            ],
            [
                self.weatherSurface,
                self.weatherBG,
                (
                    self.RADAR_WIDTH + 5,
                    self.MESSAGE_HEIGHT
                    + self.INVENTORY_HEIGHT
                    + self.INPUT_HEIGHT
                    + +self.CONSOLE_HEIGHT
                    + 2,
                ),
            ],
        ]

    def next_plane(self):
        if (
            random.randint(0, 100) <= 15
            and len(self.activeAirplanes) < ENV.MAX_AIRPLANES
            and ENV.simTime - ENV.lastPlaneInit > ENV.DELAY_NEXT_PLANE
        ):
            _model = random.choice(list(ENV.airplaneData.keys()))
            _in = True if random.randint(0, 100) <= ENV.ARRIVALS_RATIO else False
            ENV.lastPlaneInit = ENV.simTime
            self.load_new_plane(model=_model, inbound=_in)

    def load_new_plane(self, model, inbound):
        callSign = random.choice(ATC.airspaceInfo["callsigns"]) + str(
            random.randint(1000, 9999)
        )
        if inbound:
            # coordinates -- must appear from edge of airspace
            if random.randint(0, 1) < 0.5:
                x, y = (
                    float(random.randint(5, self.RADAR_WIDTH - 5)),
                    15.0 if random.randint(0, 1) < 0.5 else self.RADAR_HEIGHT - 15,
                )
            else:
                x, y = (
                    15.0 if random.randint(0, 1) < 0.5 else self.RADAR_WIDTH - 15,
                    float(random.randint(5, ENV.DISPLAY_HEIGHT - 5)),
                )
            heading = ATC.calc_heading(
                x,
                y,
                ATC.airspaceInfo["runways"][0]["headL"]["x"],
                ATC.airspaceInfo["runways"][0]["headL"]["y"],
            ) + random.randint(-30, 30)
            altitude = random.randint(5000, 8000)
            speed = random.randint(180, 300)
            isGround = False
            finalDestination = {"x": 0, "y": 0}
            runwayDeparture = "00"
            inventoryColor = ENV.GREEN
        else:
            # select random runway
            runway = random.choice(ATC.airspaceInfo["runways"])
            # select random head
            _head = runway["headL"] if ENV.windDirection < 180 else runway["headR"]
            _tail = runway["headR"] if ENV.windDirection < 180 else runway["headL"]
            x, y = (_head["x"], _head["y"])
            heading = self.calc_heading(x, y, _tail["x"], _tail["y"])
            runwayDeparture = _head["tag"]["text"]
            # plane status
            altitude = ATC.airspaceInfo["altitudes"]["groundLevel"]
            speed = 0
            isGround = True
            inventoryColor = ENV.BROWN
            # random destination
            finalDestination = random.choice(ATC.airspaceInfo["VOR"])

        # add airplane instance to active planes
        _p = Airplane(
            aircraft=model,
            callSign=callSign,
            fixedInfo=ENV.airplaneData[model],
            inventoryColor=inventoryColor,
            x=x,
            y=y,
            heading=heading,
            altitude=altitude,
            speed=speed,
            climb=0,
            turn=0,
            isInbound=inbound,
            isGround=isGround,
            runwayDeparture=runwayDeparture,
            finalDestination=finalDestination,
        )
        self.activeAirplanes.append(_p)
        # announce new plane in message box
        text = f"{callSign} {'Arriving' if inbound else f'Departing from Runway {runwayDeparture} to '+finalDestination['name']}"
        self.new_message(text=text, bgcolor=ENV.BLACK, audio=text)

    def calc_heading(self, x0, y0, x1, y1):
        a = abs(math.degrees(math.atan((y1 - y0) / (x1 - x0))))
        if x0 > x1 and y0 < y1:
            return int(270 - a)
        elif x0 < x1 and y0 < y1:
            return int(90 + a)
        elif x0 > x1 and y0 > y1:
            return int(270 + a)
        else:
            return int(90 - a)

    def new_message(self, text, bgcolor, audio):
        # written message
        self.messageText.append(
            (f"| {dt.strftime(dt.now(), '%H:%M:%S')} | {text}", dt.now(), bgcolor)
        )
        # audio message
        if ENV.audioOn and audio:
            gTTS(
                text=audio,
                lang="en",
                slow=False,
            ).save("temp.wav")
            os.system("start temp.wav")

    def next_frame(self):
        # check end-game collision
        if ENV.collision:
            print("Collision!!")
            quit()

        # process messages
        if self.messageText and dt.now() - self.messageText[0][1] > td(
            seconds=ENV.MESSAGE_DISPLAY_TIME
        ):
            self.messageText.pop(0)

        # process planes
        seqArrival = seqDeparture = 1
        for seq, plane in enumerate(self.activeAirplanes):
            self.check_proximity(plane)
            # sequential number
            plane.sequence = seq
            # calculate new x,y coordinates
            plane.x += (plane.speed / ENV.SCALE) * math.sin(math.radians(plane.heading))
            plane.y -= (plane.speed / ENV.SCALE) * math.cos(math.radians(plane.heading))
            # speed change
            if (plane.speed < plane.speedTo) and plane.onRadar:
                plane.speed = min(
                    (
                        plane.speed + plane.accelGround
                        if plane.isGround
                        else plane.speed + plane.accelAir
                    ),
                    plane.speedTo,
                )
            elif (plane.speed > plane.speedTo) and plane.onRadar:
                plane.speed = max(
                    (
                        plane.speed + plane.decelGround
                        if plane.isGround
                        else plane.speed + plane.decelAir
                    ),
                    plane.speedTo,
                )
            # only change altitude and heading if plane is airborne
            left_right = "="
            if plane.onRadar and not plane.isTakeoff and not plane.isGround:
                # altitude change
                if plane.altitude < plane.altitudeTo:
                    plane.altitude = int(
                        min(
                            (
                                plane.altitude
                                + plane.ascentRate * plane.altitudeExpedite
                            ),
                            plane.altitudeTo,
                        )
                    )
                elif plane.altitude > plane.altitudeTo:
                    plane.altitude = int(
                        max(
                            (
                                plane.altitude
                                + plane.descentRate * plane.altitudeExpedite
                            ),
                            plane.altitudeTo,
                        )
                    )
                elif plane.altitude == plane.altitudeTo:
                    plane.altitudeExpedite = 1
                # recalculate headingTo if fixed point as destination (VOR, runway head)
                if plane.goToFixed:
                    plane.headingTo = self.calc_heading(
                        plane.x, plane.y, plane.goToFixed[0], plane.goToFixed[1]
                    )
                # heading change
                clockwise = (plane.headingTo - plane.heading + 360) % 360
                anticlockwise = (plane.heading - plane.headingTo + 360) % 360
                if (
                    not plane.turnDirection and clockwise < anticlockwise
                ) or plane.turnDirection == "R":  # clockwise turn
                    plane.heading = (
                        plane.heading + plane.turnRate * plane.turnExpedite + 360
                    ) % 360
                    left_right = ">"
                elif (
                    not plane.turnDirection and anticlockwise <= clockwise
                ) or plane.turnDirection == "L":  # anticlockwise turn
                    plane.heading = (
                        plane.heading - plane.turnRate * plane.turnExpedite + 360
                    ) % 360
                    left_right = "<"
                if (
                    min(clockwise, anticlockwise) <= plane.turnRate
                ):  # end of turn (reached desired heading)
                    plane.heading = plane.headingTo
                    plane.turnDirection = None
                    left_right = "="
                    plane.turnExpedite = 1

            # check for ordered to head/takeoff and taxi time to get there
            if plane.taxiTime > 0:
                plane.taxiTime -= 1
                if plane.taxiTime == 0:
                    plane.onRadar = True

            # check for end of takeoff conditions
            if plane.isTakeoff and plane.speed >= plane.speedTakeoff:
                plane.isTakeoff = False
                plane.isGround = False
                plane.inventoryColor = ENV.GREEN

            # check if plane on ILS intercept course hits ILS glide scope and begin landing
            if plane.ILSIntercept and int(
                self.calc_heading(
                    plane.x, plane.y, plane.ILSIntercept[0], plane.ILSIntercept[1]
                )
            ) == int(plane.ILSIntercept[2]):
                plane.isLanding = True
                # new heading to fixed point (runway head)
                plane.goToFixed = (plane.ILSIntercept[0], plane.ILSIntercept[1])
                # new speed set to landing speed
                plane.speedTo = plane.speedLanding
                # new altitude is runway head altitude
                plane.altitudeTo = ATC.airspaceInfo["altitudes"]["groundLevel"]
                # update inventory color
                plane.inventoryColor = ENV.BLUE

            # recalculate descent rate if plane is landing
            if plane.isLanding and not plane.isGround:
                _s = math.sqrt(
                    (plane.x - plane.goToFixed[0]) ** 2
                    + (plane.y - plane.goToFixed[1]) ** 2
                )

                # plane cannot descent faster than max descent rate
                plane.descentRate = max(
                    plane.descentRate,
                    -(plane.altitude - plane.altitudeTo)
                    / (_s / (plane.speed / ENV.SCALE)),
                )

                # check if touchdown (safe or go-around)
                x, y = plane.goToFixed
                # arrived at coordinates for land/go-around decision
                if (
                    x - 2 <= int(plane.x) <= x + 2
                    and y - 2 <= int(plane.y) <= y + 2
                    and plane.isLanding
                    and not plane.isGround
                ):
                    # land
                    if (
                        plane.altitude
                        <= ATC.airspaceInfo["altitudes"]["groundLevel"] + 100
                        and plane.speed <= plane.speedLanding + 3
                    ):
                        plane.heading = plane.runwayHeading
                        plane.speedTo = 0
                        plane.isGround = True
                    else:  # go-around
                        plane.altitudeTo = self.airspaceInfo["altitudes"]["goAround"]
                        plane.speedTo = plane.speedCruise
                        plane.goToFixed = False
                        plane.directionTo = plane.heading
                        plane.isLanding = False
                        plane.inventoryColor = ENV.GREEN
                        self.new_message(
                            text=f"Unsafe Landing Conditions. Go Around. [-1 POINTS]",
                            bgcolor=ENV.RED,
                            audio="",
                        )
                        ENV.score["goArounds"] -= 1

            # random plane declares emergency
            if random.randint(0, 100000) <= ENV.EMERGENCY_CHANCE:
                plane.isPriority = True
                plane.inventoryColor = ENV.RED

            # calculate time on inventory
            plane.timeActive = ENV.simTime - plane.timeInit

            # update pygame moving entities info - Radar screen
            plane.boxPosition = plane.boxSurface.get_rect(center=(plane.x, plane.y))
            plane.tailPosition0 = (plane.x, plane.y)
            plane.tailPosition1 = (
                plane.x
                + (plane.speed // 20 + 4) * math.sin(math.radians(plane.heading + 180)),
                plane.y
                - (plane.speed // 20 + 4) * math.cos(math.radians(plane.heading + 180)),
            )
            up_down = (
                chr(8593)
                if plane.altitude < plane.altitudeTo
                else chr(8595)
                if plane.altitude > plane.altitudeTo
                else "="
            )
            plane.tagText0 = ENV.FONT12.render(
                plane.callSign, True, plane.tagColor, ENV.BG
            )
            plane.tagText1 = ENV.FONT12.render(
                f"{(plane.altitude // 100):03}{up_down}{int(plane.speed/10)}",
                True,
                plane.tagColor,
                ENV.BG,
            )
            plane.tagPosition0 = (plane.x + 20, plane.y + 20)
            plane.tagPosition1 = (plane.x + 20, plane.y + 33)
            plane.tagClickArea = pygame.Rect(
                plane.tagPosition0[0], plane.tagPosition0[1], 42, 26
            )
            # update inventory item
            plane.inventoryText = pygame.Surface((ATC.CONTROLS_WIDTH // 2 - 7, 37))
            plane.inventoryText.fill(plane.inventoryColor)
            accel = (
                chr(8593)
                if plane.speed < plane.speedTo
                else chr(8595)
                if plane.speed > plane.speedTo
                else "="
            )
            plane.inventoryText.blit(
                ENV.FONT12.render(
                    f"{plane.callSign}  {f'{plane.headingTo:03}°' if not plane.goToFixed else plane.goToFixedName}{left_right}  {plane.altitudeTo} {up_down}  {plane.speedTo} {accel}",
                    True,
                    ENV.WHITE,
                    plane.inventoryColor,
                ),
                dest=(5, 5),
            )
            plane.inventoryText.blit(
                ENV.FONT12.render(
                    f"{plane.aircraft}  {'Arrival' if plane.isInbound else f'Departure from {plane.runwayDeparture}  --> ' + plane.finalDestination['name']}          [{str(plane.timeActive)[:-7]}]",
                    True,
                    ENV.WHITE,
                    plane.inventoryColor,
                ),
                dest=(5, 20),
            )
            if plane.isInbound:
                _seq = seqArrival
                seqArrival += 1
            else:
                _seq = seqDeparture
                seqDeparture += 1
            plane.inventoryPosition = (5, _seq * 42 + 2)

            plane.inventoryClickArea = pygame.Rect(
                self.RADAR_WIDTH + (0 if plane.isInbound else self.CONTROLS_WIDTH // 2),
                self.MESSAGE_HEIGHT + _seq * 42 + 2,
                self.CONTROLS_WIDTH // 2,
                40,
            )

            # check for safe landing
            x, y = plane.finalDestination["x"], plane.finalDestination["y"]
            if plane.isInbound:
                if plane.isGround and plane.speed == 0:
                    ATC.activeAirplanes.remove(plane)
                    ENV.score["arrivals"] += 1
                    self.new_message(
                        text=f"{plane.callSign} contact ground control at 132.5. Welcome. [+1 POINTS]",
                        bgcolor=ENV.GREEN,
                        audio="",
                    )
            # check for safe VOR arrival
            elif (
                x - 10 <= int(plane.x) <= x + 10
                and y - 10 <= int(plane.y) <= y + 10
                and plane.altitude >= ATC.airspaceInfo["altitudes"]["handOff"]
            ):
                ATC.activeAirplanes.remove(plane)
                ENV.score["departures"] += 1
                self.new_message(
                    text=f"{plane.callSign} contact air control at 183.4. Goodbye. [+1 POINTS]",
                    bgcolor=ENV.GREEN,
                    audio="",
                )
            # check for unsafe airspace exit
            if (
                plane.x < 0
                or plane.x > ATC.RADAR_WIDTH
                or plane.y < 0
                or plane.y > ATC.RADAR_HEIGHT
            ):
                ATC.activeAirplanes.remove(plane)
                ENV.score["uncontrolledExits"] -= 1
                self.new_message(
                    text=f"{plane.callSign} uncontrolled exit from airspace. [-1 POINTS]",
                    bgcolor=ENV.RED,
                    audio="",
                )

        # process timer
        ENV.simTime += dt.now() - ENV.simTimeSplit
        ENV.simTimeSplit = dt.now()

    def check_proximity(self, plane):
        for other_plane in ATC.activeAirplanes:
            if (
                not plane == other_plane
                and not plane.isGround
                and not other_plane.isGround
            ):
                dist = math.sqrt(
                    (plane.x - other_plane.x) ** 2 + (plane.y - other_plane.y) ** 2
                )
                # collision detection
                if (
                    abs(plane.altitude - other_plane.altitude)
                    < ENV.MIN_V_SEPARATION * 0.15
                    and dist < ENV.MIN_H_SEPARATION * 0.15
                ):
                    ENV.collision = True
                    return
                # warning detection
                if (
                    abs(plane.altitude - other_plane.altitude) < ENV.MIN_V_SEPARATION
                    and dist < ENV.MIN_H_SEPARATION
                    and not plane.isLanding
                    and not other_plane.isLanding
                ):
                    plane.tagColor = ENV.RED
                    ENV.score["warnings"] = round(ENV.score["warnings"] - 0.1, 1)
                    return
                else:
                    plane.tagColor = ENV.WHITE


class Airplane(pygame.sprite.Sprite):
    def __init__(self, **kw):
        super().__init__()
        # airplance fixed characteristics
        self.aircraft = kw["aircraft"]
        self.callSign = kw["callSign"]
        self.inventoryColor = kw["inventoryColor"]
        self.speedMin = kw["fixedInfo"]["speed"]["min"]
        self.speedMax = kw["fixedInfo"]["speed"]["max"]
        self.speedCruise = kw["fixedInfo"]["speed"]["cruising"]
        self.speedLanding = kw["fixedInfo"]["speed"]["landing"]
        self.speedTakeoff = kw["fixedInfo"]["speed"]["takeoff"]
        self.ascentRate = kw["fixedInfo"]["ascentRate"]
        self.descentRate = kw["fixedInfo"]["descentRate"]
        self.turnRate = kw["fixedInfo"]["turnRate"]
        self.accelGround = kw["fixedInfo"]["acceleration"]["ground"]
        self.accelAir = kw["fixedInfo"]["acceleration"]["air"]
        self.decelGround = kw["fixedInfo"]["deceleration"]["ground"]
        self.decelAir = kw["fixedInfo"]["deceleration"]["air"]
        self.altitudeApproach = kw["fixedInfo"]["altitude"]["approach_max"]
        self.altitudeMax = kw["fixedInfo"]["altitude"]["ceiling"]
        self.altitudeMin = kw["fixedInfo"]["altitude"]["floor"]
        self.timeInit = ENV.simTime
        self.timeActive = 0
        # airplane position
        self.x = kw["x"]
        self.y = kw["y"]
        self.heading = kw["heading"]
        self.altitude = kw["altitude"]
        # airplane position change
        self.speed = kw["speed"]
        self.climb = kw["climb"]
        self.turn = kw["turn"]
        # airplane destination
        self.speedTo = self.speed
        self.altitudeTo = self.altitude
        self.headingTo = self.heading
        self.turnDirection = None
        self.goToFixed = False
        self.finalDestination = kw["finalDestination"]
        # airplane status
        self.isLanding = False
        self.ILSIntercept = False
        self.isInbound = kw["isInbound"]
        self.isGround = kw["isGround"]
        self.onRadar = True if self.isInbound else False
        self.isTakeoff = False
        self.isPriority = False
        self.runwayDeparture = kw["runwayDeparture"]
        self.taxiTime = 0
        self.turnExpedite = 1
        self.altitudeExpedite = 1
        # create pygame entity - airplane box
        self.boxSurface = pygame.Surface((9, 9))
        pygame.draw.rect(self.boxSurface, ENV.WHITE, (0, 0, 8, 8), width=1)
        self.boxPosition = (-10, -10)  # dummy data
        # create pygame entity - airplane tail
        self.tailPosition0 = (0, 0)
        self.tailPosition1 = (0, 0)
        # default tag text color
        self.tagColor = ENV.WHITE
        # create pygame entities (dummy data)
        self.tagText0 = self.tagText1 = self.inventoryText = ENV.FONT12.render(
            " ",
            True,
            ENV.WHITE,
            ENV.BG,
        )
        self.tagPosition0 = self.tagPosition1 = self.inventoryPosition = (
            self.x + 20,
            self.y + 20,
        )
        self.tagClickArea = pygame.Rect(0, 0, 0, 0)
        self.inventoryClickArea = pygame.Rect(0, 0, 0, 0)


def process_click(pos):
    for plane in ATC.activeAirplanes:
        if plane.inventoryClickArea.collidepoint(
            pos
        ) or plane.tagClickArea.collidepoint(pos):
            ATC.commandText = plane.callSign + " "
            return


def process_keydown(key):
    if key == 27:
        pop_up(action="QUIT", pause=0)
    if ATC.commandText in ENV.ERRORS:
        ATC.commandText = ""
    if 97 <= key <= 122 or 48 <= key <= 57 or key == K_SPACE:  # A - Z + 0 - 9
        ATC.commandText += chr(key).upper()
    if key in ENV.NUMPAD_KEYS:
        ATC.commandText += ENV.NUMPAD_KEYS[key]
    elif key == K_BACKSPACE:
        ATC.commandText = ATC.commandText[:-1]
    elif key in (K_KP_ENTER, K_RETURN):
        process_command()
    elif key in (K_LCTRL, K_RCTRL):
        ATC.commandText = ATC.lastCallSign
    elif key in ENV.FUNCTION_KEYS:
        fkey = ENV.FUNCTION_KEYS[key]
        if fkey == "F1":
            pop_up(action="HELP", pause=1)
        if fkey == "F2":
            ENV.tagActive = False if ENV.tagActive == True else True
            pop_up(action="TOGGLE", pause=1)
        if fkey == "F3":
            ENV.guidelineActive = False if ENV.guidelineActive == True else True
            pop_up(action="TOGGLE", pause=1)
        if fkey == "F4":
            ENV.audioOn = False if ENV.audioOn == True else True
            pop_up(action="TOGGLE", pause=1)
        if fkey == "F5":
            pop_up(action=None, pause=0)

    elif key == K_TAB:  # testing only
        ENV.SPEED = 5 if ENV.SPEED == 1 else 1


def process_command():
    error = False
    # if empty command or no planes active
    if not ATC.commandText or not ATC.activeAirplanes:
        return

    # parse: clean extra spaces
    while "  " in ATC.commandText:
        ATC.commandText = ATC.commandText.replace("  ", " ")
    # TODO: parse: add necessary spaces after valid command

    # extract flight number
    flt, *cmd = ATC.commandText.split(" ")
    # check if flight number exists
    plane = [i for i in ATC.activeAirplanes if i.callSign == flt]
    if plane:
        plane = plane[0]
        ATC.lastCallSign = plane.callSign + " "
    else:
        ATC.commandText = ""
        cmd = ""
        error = 3

    # check if format is right (2 or 3 blocks of commands)
    bgcolor_text = ENV.BLACK
    if len(cmd) == 1 and not error:
        if cmd[0] == "H":
            # go to runway head
            if not plane.onRadar:
                plane.taxiTime = random.randint(8, 15)
                # plane.onRadar = True
                text = f"{plane.callSign} Proceed to runway and await clearance."
            else:
                error = 2

        elif cmd[0] == "T":
            # full takeoff
            if not plane.onRadar or (plane.onRadar and plane.speed == 0):
                plane.taxiTime = random.randint(8, 15)
                # plane.onRadar = True
                plane.speedTo = (
                    plane.speedCruise if not plane.speedTo else plane.speedTo
                )
                plane.isTakeoff = True
                plane.altitudeTo = max(
                    plane.altitudeTo, ATC.airspaceInfo["altitudes"]["groundLevel"] + 500
                )
                text = f"{plane.callSign} Cleared for Takeoff"
            else:
                error = 2

        elif cmd[0] == "Q" or cmd[0] == "ABORT":  # abort landing clearance
            if plane.isLanding:
                plane.isLanding = False
                plane.speedTo = plane.speedCruise
                plane.altitudeTo = ATC.airspaceInfo["altitudes"]["goAround"]
                text = f"{plane.callSign} Landing Clearance Cancelled"
            elif plane.ILSIntercept:
                plane.ILSIntercept = False
                text = f"{plane.callSign} Landing Clearance Cancelled"
            else:
                error = 1

        elif cmd[0] == "X":  # only for testing
            plane.isPriority = True
            plane.inventoryColor = ENV.RED
            text = f"{plane.callSign} Declaring Emergency"

        elif cmd[0] == "INFO":  # display plane model information
            text = f"{plane.callSign} INFO - Min Speed: {plane.speedMin} - Max Soeed: {plane.speedMax}"

        else:
            error = 1

    elif len(cmd) > 1 and not plane.isLanding and not error:
        if cmd[0] == "C":  # change heading to fixed number or VOR
            if cmd[1].isdigit() and 0 <= int(cmd[1]) <= 360:  # chose fixed heading
                plane.headingTo = int(cmd[1])
                plane.goToFixed = False
                _cwise = (plane.headingTo - plane.heading + 360) % 360
                _acwise = (plane.heading - plane.headingTo + 360) % 360
                text = f'{plane.callSign} turn {"left" if _cwise>=_acwise else "right"} to heading {int(cmd[1]):03d}°'
                if len(cmd) > 2 and cmd[2] in ("R", "L"):
                    plane.turnDirection = cmd[2]
                    text = f'{plane.callSign} turn {"left" if cmd[2]=="L" else "right"} to heading {int(cmd[1]):03d}°'
                if len(cmd) > 2 and cmd[2] == "X":
                    bgcolor_text, text = process_expedite(plane, text)
            elif cmd[1].isalpha() and cmd[1] in [
                i["name"] for i in ATC.airspaceInfo["VOR"]
            ]:  # chose VOR
                VORxy = [
                    (i["x"], i["y"])
                    for i in ATC.airspaceInfo["VOR"]
                    if i["name"] == cmd[1]
                ][0]
                plane.goToFixed = (VORxy[0], VORxy[1])
                plane.goToFixedName = cmd[1].strip()
                text = f"{plane.callSign} Head to {plane.goToFixedName}"
                if len(cmd) > 2 and cmd[2] in ("R", "L"):
                    plane.turnDirection = cmd[2]
                if len(cmd) > 2 and cmd[2] == "X":
                    bgcolor_text, text = process_expedite(plane, text)
            else:
                error = 2
        elif cmd[0] == "A" and cmd[1].isdigit():  # change altitude
            new = int(cmd[1])
            if (
                ATC.airspaceInfo["altitudes"]["groundLevel"] + 500
                <= new * 1000
                <= plane.altitudeMax
            ):
                plane.altitudeTo = new * 1000
                text = f"{plane.callSign} {'Climb' if plane.altitudeTo>plane.altitude else 'Descend'} and Maintain {new*1000:,} feet"
                if len(cmd) > 2 and cmd[2] == "X":
                    bgcolor_text, text = process_expedite(plane, text)
            else:
                error = 2
        elif cmd[0] == "S" and cmd[1].isdigit():  # change speed
            if plane.speedMin <= int(cmd[1]) <= plane.speedMax:
                plane.speedTo = int(cmd[1])
                text = f"{plane.callSign} New speed {int(cmd[1])}"
            else:
                error = 2

        elif cmd[0] == "L" and cmd[1].isdigit():
            _runways = []
            for i in ("headL", "headR"):
                for s in ATC.airspaceInfo["runways"]:
                    _runways.append(s[i])

            selected_runway = [
                ((i["x"], i["y"]), i["heading"])
                for i in _runways
                if i["tag"]["text"] == cmd[1]
            ]

            if selected_runway:
                # landing condition: must be at or below approach altitude
                altitude_check = plane.altitude <= plane.altitudeApproach
                # landing condition: must be heading within certain degress from runqay headinng
                plane.runwayHeading = selected_runway[0][1]

                delta_heading = abs(plane.heading - plane.runwayHeading)
                delta_heading = (
                    360 - delta_heading if delta_heading > 180 else delta_heading
                )
                heading_check = delta_heading <= ENV.ILS_HEADING
                if all([altitude_check, heading_check, plane.isInbound]):
                    plane.ILSIntercept = (
                        selected_runway[0][0][0],
                        selected_runway[0][0][1],
                        selected_runway[0][1],
                    )
                    plane.goToFixedName = f"Runway {cmd[1]} "
                    # new altitude target is runway head altitude
                    text = (
                        f"{plane.callSign} Cleared to Intercept ILS for Runway {cmd[1]}"
                    )
                    plane.inventoryColor = ENV.LIGHT_BLUE
                else:
                    error = 2
            else:
                error = 1
        else:
            error = 1
    else:
        error = max(1, error)

    if error:
        ATC.commandText = ENV.ERRORS[error]
    else:
        ATC.new_message(text=text, bgcolor=bgcolor_text, audio=text)
        ATC.commandText = ""


def process_expedite(plane, text):
    text += ". Expedite!"
    bgcolor_text = ENV.RED
    ENV.score["expediteCommands"] = round(ENV.score["expediteCommands"] - 0.2, 1)
    plane.altitudeExpedite = 2
    return bgcolor_text, text


def render_table(surface, table_data, width, height):
    left_margin = 30
    top_margin = 50
    rows = len(table_data)
    cols = len(table_data[0])
    cell_width = (width - left_margin * 2) // cols
    cell_height = (height - top_margin * 2) // rows
    for row, row_data in enumerate(table_data):
        for col, col_data in enumerate(row_data):
            table = pygame.Surface((cell_width, cell_height))
            table.fill(ENV.BLACK)
            render_text(
                surface=table,
                font=ENV.FONT12,
                text=[(col_data)],
                fgColor=ENV.WHITE,
            )
            surface.blit(
                source=table,
                dest=(cell_width * col + left_margin, cell_height * row + top_margin),
            )


def render_text(surface, font, text, fgColor, x0=0, y0=0, dy=0):
    for deltay, line in enumerate(text):
        _t = font.render(line[0], True, fgColor, line[1])
        surface.blit(source=_t, dest=(x0, y0 + deltay * dy))


def update_pygame_display():
    # load all level-2 background surfaces to reset screen
    for surfaces in ATC.allLevel2Surfaces:
        surfaces[0].blit(source=surfaces[1], dest=(0, 0))
    # ILS projection lines (toggle)
    if ENV.guidelineActive:
        for runway in ATC.airspaceInfo["runways"]:
            for head in ("headL", "headR"):
                _x = runway[head]["x"] - (
                    math.cos(math.radians(runway[head]["heading"] - 90)) * 1000
                )
                _y = runway[head]["y"] - (
                    math.sin(math.radians(runway[head]["heading"] - 90)) * 1000
                )
                pygame.draw.line(
                    ATC.radarSurface,
                    ENV.GRAY,
                    (runway[head]["x"], runway[head]["y"]),
                    (_x, _y),
                    width=runway["width"],
                )

    # load Radar main surface + Inventory main surface
    for entity in ATC.activeAirplanes:
        if entity.onRadar:
            ATC.radarSurface.blit(source=entity.boxSurface, dest=entity.boxPosition)
            pygame.draw.line(
                ATC.radarSurface, ENV.RED, entity.tailPosition0, entity.tailPosition1
            )
            if ENV.tagActive:
                ATC.radarSurface.blit(source=entity.tagText0, dest=entity.tagPosition0)
                ATC.radarSurface.blit(source=entity.tagText1, dest=entity.tagPosition1)
        if entity.isInbound:
            ATC.inventoryArrivalsSurface.blit(
                source=entity.inventoryText, dest=entity.inventoryPosition
            )
        else:
            ATC.inventoryDeparturesSurface.blit(
                source=entity.inventoryText, dest=entity.inventoryPosition
            )
    # load Message main surface
    render_text(
        surface=ATC.messageSurface,
        font=ENV.FONT12,
        text=[(i[0], i[2]) for i in ATC.messageText],
        fgColor=ENV.WHITE,
        x0=5,
        y0=4,
        dy=15,
    )
    # load Input Command main surface
    render_text(
        surface=ATC.inputSurface,
        font=ENV.FONT20,
        text=[(ATC.commandText, ENV.WHITE)],
        fgColor=ENV.BLACK,
        x0=5,
        y0=20,
    )
    # load Weather main surface
    _text = [
        (f"GMT: {dt.strftime(dt.now(),'%H:%M:%S')}", ENV.BG_CONTROLS),
        (f"Wind: {ENV.windSpeed} knots @ {ENV.windDirection:03}°.", ENV.BG_CONTROLS),
        (f"Simulation Time: {str(ENV.simTime)[:-7]}.", ENV.BG_CONTROLS),
        (f"Airspace Information:", ENV.BG_CONTROLS),
        (
            f"Ground Level: {ATC.airspaceInfo['altitudes']['groundLevel']} feet.",
            ENV.BG_CONTROLS,
        ),
        (
            f"Handoff Altitude: {ATC.airspaceInfo['altitudes']['handOff']} feet.",
            ENV.BG_CONTROLS,
        ),
    ]
    render_text(
        surface=ATC.weatherSurface,
        font=ENV.FONT14,
        text=_text,
        fgColor=ENV.WHITE,
        x0=10,
        y0=25,
        dy=30,
    )

    # load Console main surface
    ENV.score["total"] = round(
        (
            ENV.score["departures"]
            + ENV.score["arrivals"]
            + ENV.score["expediteCommands"]
            + ENV.score["uncontrolledExits"]
            + ENV.score["warnings"]
            + ENV.score["goArounds"]
        ),
        1,
    )
    text = [
        [(f"{j.title()}", ENV.BLACK), (f"{str(i)}", ENV.BLACK)]
        for i, j in zip(ENV.score.values(), ENV.SCORE_TITLES)
    ]

    render_table(
        surface=ATC.consoleSurface,
        table_data=text,
        width=ATC.CONTROLS_WIDTH,
        height=ATC.CONSOLE_HEIGHT,
    )
    # load all level-2 main surfaces
    for surfaces in ATC.allLevel2Surfaces:
        ATC.displaySurface.blit(source=surfaces[0], dest=surfaces[2])

    pygame.display.update()


def pop_up(action, pause):
    # define text that goes in popup
    if action == "HELP":
        message = ENV.FONT12.render("Help Text", True, ENV.BLACK, ENV.WHITE)
    elif action == "QUIT":
        message = ENV.FONT12.render(
            "ENTER to quit. Any other key to continue.", True, ENV.BLACK, ENV.WHITE
        )
    elif action == "TOGGLE":
        message = ENV.FONT20.render("TOGGLE", True, ENV.BLACK, ENV.WHITE)
    # create popup and display
    popupSizex, popupSizey = 500, 100
    popUpSurface = pygame.Surface((popupSizex, popupSizey))
    popUpSurface.fill(ENV.WHITE)
    title = ENV.FONT20.render("GAME PAUSED", True, ENV.RED, ENV.WHITE)
    popUpSurface.blit(source=title, dest=((popupSizex - title.get_width()) // 2, 10))
    popUpSurface.blit(
        source=message, dest=((popupSizex - message.get_width()) // 2, 50)
    )
    ATC.displaySurface.blit(
        source=popUpSurface,
        dest=(ENV.DISPLAY_WIDTH // 2 - 250, ENV.DISPLAY_HEIGHT // 2 - 100),
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
                        ENV.simTimeSplit = dt.now()
                        return


def main():
    clock = pygame.time.Clock()
    delay = ENV.FPS // ENV.SPEED
    while True:
        clock.tick(ENV.FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                quit()
            elif event.type == KEYDOWN:
                process_keydown(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                process_click(pos=pygame.mouse.get_pos())
        update_pygame_display()
        # actions happen with regulated frequency
        delay -= 1
        if delay == 0:
            ATC.next_frame()
            ATC.next_plane()
            delay = ENV.FPS // ENV.SPEED


ENV = Environment(sys.argv)
ATC = Airspace()
main()
