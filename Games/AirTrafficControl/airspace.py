import os
import json
import math
import random
import pygame
from pygame.locals import *
from datetime import datetime as dt, timedelta as td
import airplane
from gtts import gTTS


class Airspace:
    def __init__(self, ENV) -> None:
        self.ENV = ENV
        # load plane tech spec data from json file
        self.activeAirplanes = []
        self.lastCallSign = ""
        self.init_pygame()

    def init_pygame(self):
        # pygame init
        os.environ["SDL_VIDEO_WINDOW_POS"] = "1, 1"
        self.displaySurface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.RADAR_WIDTH = int(self.ENV.DISPLAY_WIDTH * 0.75)
        self.RADAR_HEIGHT = self.ENV.DISPLAY_HEIGHT
        self.CONTROLS_WIDTH = int(self.ENV.DISPLAY_WIDTH * 0.25)
        self.MESSAGE_HEIGHT = int(self.ENV.DISPLAY_HEIGHT * 0.1)
        self.INVENTORY_HEIGHT = int(self.ENV.DISPLAY_HEIGHT * 0.45)
        self.INPUT_HEIGHT = int(self.ENV.DISPLAY_HEIGHT * 0.05)
        self.CONSOLE_HEIGHT = int(self.ENV.DISPLAY_HEIGHT * 0.2)
        self.WEATHER_HEIGHT = int(self.ENV.DISPLAY_HEIGHT * 0.2)

        pygame.display.set_caption("ATC Simulator")

    def init_load_airspace(self):
        with open("atc-airspace.json", mode="r") as json_file:
            self.airspaceInfo = json.loads(json_file.read())
        # create VOR shape entities
        triangle = pygame.Surface((10, 10))
        triangle.fill(self.ENV.BG)
        pygame.draw.polygon(triangle, self.ENV.WHITE, ((5, 0), (0, 9), (9, 9)), True)
        circles = pygame.Surface((10, 10))
        circles.fill(self.ENV.BG)
        pygame.draw.circle(circles, self.ENV.WHITE, (5, 5), 5, True)
        pygame.draw.circle(circles, self.ENV.WHITE, (5, 5), 3, True)
        star = pygame.Surface((10, 10))
        star.fill(self.ENV.BG)
        _s = ((5, 1), (7, 4), (9, 5), (7, 6), (5, 9), (3, 6), (1, 5), (3, 4), (5, 1))
        pygame.draw.polygon(star, self.ENV.WHITE, _s, True)
        symbols = {"TRIANGLE": triangle, "CIRCLES": circles, "STAR": star}

        # create Radar main and background surfaces
        self.radarSurface = pygame.Surface(
            (self.ENV.DISPLAY_WIDTH, self.ENV.DISPLAY_HEIGHT)
        )
        self.radarSurface.fill(self.ENV.BG)
        self.radarBG = pygame.Surface.copy(self.radarSurface)
        # add VOR entities to Radar background surface
        for vor in self.airspaceInfo["VOR"]:
            self.radarBG.blit(
                source=symbols[vor["symbol"]], dest=((vor["x"], vor["y"]))
            )
            self.radarBG.blit(
                source=self.ENV.FONT14.render(
                    vor["name"],
                    True,
                    self.ENV.WHITE,
                    self.ENV.BG,
                ),
                dest=(vor["x"] + 14, vor["y"] - 3),
            )
        # add Runway entities to Radar background surface
        for runway in self.airspaceInfo["runways"]:
            pygame.draw.line(
                self.radarBG,
                self.ENV.WHITE,
                (runway["headL"]["x"], runway["headL"]["y"]),
                (runway["headR"]["x"], runway["headR"]["y"]),
                width=runway["width"],
            )
            for d in ("headL", "headR"):
                self.radarBG.blit(
                    source=self.ENV.FONT14.render(
                        runway[d]["tag"]["text"], True, self.ENV.WHITE, self.ENV.BG
                    ),
                    dest=runway[d]["tag"]["xy"],
                )

    def next_plane(self):
        if len(self.activeAirplanes) == 0 or (
            random.randint(0, 100) <= 15
            and len(self.activeAirplanes) < self.ENV.MAX_AIRPLANES
            and self.ENV.simTime - self.ENV.lastPlaneInit > self.ENV.DELAY_NEXT_PLANE
        ):
            _model = random.choice(list(self.ENV.airplaneData.keys()))
            _in = True if random.randint(0, 100) <= self.ENV.ARRIVALS_RATIO else False
            self.ENV.lastPlaneInit = self.ENV.simTime
            self.load_new_plane(model=_model, inbound=_in)

    def load_new_plane(self, model, inbound):
        callSign = random.choice(self.airspaceInfo["callsigns"]) + str(
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
                    float(random.randint(5, self.ENV.DISPLAY_HEIGHT - 5)),
                )
            heading = self.calc_heading(
                x,
                y,
                self.airspaceInfo["runways"][0]["headL"]["x"],
                self.airspaceInfo["runways"][0]["headL"]["y"],
            ) + random.randint(-30, 30)
            altitude = random.randint(5000, 8000)
            speed = random.randint(180, 300)
            isGround = False
            finalDestination = {"x": 0, "y": 0}
            runwayDeparture = "00"
            inventoryColor = self.ENV.GREEN
            willMissApproach = (
                True if random.random() < self.ENV.CHANCE_MISSED_APPROACH else False
            )
            willDeclareEmergency = (
                True if random.random() < self.ENV.CHANCE_EMERGENCY else False
            )

        else:
            # select random runway
            runway = random.choice(self.airspaceInfo["runways"])
            # select random head
            _head = runway["headL"] if self.ENV.windDirection < 180 else runway["headR"]
            _tail = runway["headR"] if self.ENV.windDirection < 180 else runway["headL"]
            x, y = (_head["x"], _head["y"])
            heading = self.calc_heading(x, y, _tail["x"], _tail["y"])
            runwayDeparture = _head["tag"]["text"]
            # plane status
            altitude = self.airspaceInfo["altitudes"]["groundLevel"]
            speed = 0
            isGround = True
            inventoryColor = self.ENV.BROWN
            # random destination
            finalDestination = random.choice(self.airspaceInfo["VOR"])
            willMissApproach = False
            willDeclareEmergency = False

        # add airplane instance to active planes
        _p = airplane.Airplane(
            aircraft=model,
            callSign=callSign,
            fixedInfo=self.ENV.airplaneData[model],
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
            willMissApproach=willMissApproach,
            willDeclareEmergency=willDeclareEmergency,
            ENV=self.ENV,
        )
        self.activeAirplanes.append(_p)
        # announce new plane in message box
        text = f"{callSign} {'Arriving' if inbound else f'Departing from Runway {runwayDeparture} to '+finalDestination['name']}"
        self.new_message(text=text, bgcolor=self.ENV.BLACK, audio=text)

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
        if self.ENV.audioOn and audio:
            gTTS(
                text=audio,
                lang="en",
                slow=False,
            ).save("temp.wav")
            os.system("start temp.wav")

    def next_frame(self):
        # check end-game collision
        if self.ENV.collision:
            print("Collision!!")
            quit()

        # process messages
        if self.messageText and dt.now() - self.messageText[0][1] > td(
            seconds=self.ENV.MESSAGE_DISPLAY_TIME
        ):
            self.messageText.pop(0)

        # process planes
        seqArrival = seqDeparture = 1
        for seq, plane in enumerate(self.activeAirplanes):
            self.check_proximity(plane)
            # sequential number
            plane.sequence = seq
            # calculate new x,y coordinates
            plane.x += (plane.speed / self.ENV.SCALE) * math.sin(
                math.radians(plane.heading)
            )
            plane.y -= (plane.speed / self.ENV.SCALE) * math.cos(
                math.radians(plane.heading)
            )
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
                # heading change (only if post-take off completed)
                if not plane.isPostTakeoff:
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
                if not plane.isPriority:
                    plane.inventoryColor = self.ENV.GREEN

            # check for end of post-takeoff conditions
            if (
                plane.isPostTakeoff
                and plane.altitude >= self.airspaceInfo["altitudes"]["postTakeoff"]
            ):
                plane.isPostTakeoff = False

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
                plane.altitudeTo = self.airspaceInfo["altitudes"]["groundLevel"]
                # update inventory color
                plane.inventoryColor = self.ENV.BLUE

            # recalculate descent rate if plane is landing
            if plane.isLanding and not plane.isGround:
                _s = math.sqrt(
                    (plane.x - plane.goToFixed[0]) ** 2
                    + (plane.y - plane.goToFixed[1]) ** 2
                )

                # plane cannot descend faster than max descent rate
                plane.descentRate = max(
                    plane.descentRate,
                    -(plane.altitude - plane.altitudeTo)
                    / (_s / (plane.speed / self.ENV.SCALE)),
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
                        <= self.airspaceInfo["altitudes"]["groundLevel"] + 100
                        and plane.speed <= plane.speedLanding + 3
                        and not plane.willMissApproach
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
                        plane.inventoryColor = self.ENV.GREEN
                        if plane.willMissApproach:
                            self.new_message(
                                text=f"Pilot Aborted Landing. Go Around.",
                                bgcolor=self.ENV.RED,
                                audio="",
                            )
                            plane.willMissApproach = False
                        else:
                            self.new_message(
                                text=f"Unsafe Landing Conditions. Go Around. [-1 POINTS]",
                                bgcolor=self.ENV.RED,
                                audio="",
                            )
                            self.ENV.score["goArounds"] -= 1

            # plane declares emergency (must have been pre-selected)
            if plane.willDeclareEmergency and random.random() <= 0.1:
                plane.isPriority = True
                plane.inventoryColor = self.ENV.RED

            # calculate time on inventory
            plane.timeActive = self.ENV.simTime - plane.timeInit

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
                else chr(8595) if plane.altitude > plane.altitudeTo else "="
            )
            plane.tagText0 = self.ENV.FONT12.render(
                plane.callSign, True, plane.tagColor, self.ENV.BG
            )
            plane.tagText1 = self.ENV.FONT12.render(
                f"{(plane.altitude // 100):03}{up_down}{int(plane.speed/10)}",
                True,
                plane.tagColor,
                self.ENV.BG,
            )
            plane.tagPosition0 = (
                plane.x + self.ENV.tagDeltaX,
                plane.y + self.ENV.tagDeltaY,
            )
            plane.tagPosition1 = (
                plane.x + self.ENV.tagDeltaX,
                plane.y + self.ENV.tagDeltaY + 13,
            )
            plane.tagClickArea = pygame.Rect(
                plane.tagPosition0[0], plane.tagPosition0[1], 42, 26
            )
            # update inventory item
            plane.inventoryText = pygame.Surface((self.CONTROLS_WIDTH // 2 - 7, 37))
            plane.inventoryText.fill(plane.inventoryColor)
            accel = (
                chr(8593)
                if plane.speed < plane.speedTo
                else chr(8595) if plane.speed > plane.speedTo else "="
            )
            plane.inventoryText.blit(
                self.ENV.FONT12.render(
                    f"{plane.callSign}  {f'{plane.headingTo:03}°' if not plane.goToFixed else plane.goToFixedName}{left_right}  {plane.altitudeTo} {up_down}  {plane.speedTo} {accel}",
                    True,
                    self.ENV.WHITE,
                    plane.inventoryColor,
                ),
                dest=(5, 5),
            )
            plane.inventoryText.blit(
                self.ENV.FONT12.render(
                    f"{plane.aircraft}  {'Arrival' if plane.isInbound else f'Departure from {plane.runwayDeparture}  --> ' + plane.finalDestination['name']}          [{str(plane.timeActive)[:-7]}]",
                    True,
                    self.ENV.WHITE,
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
                    self.activeAirplanes.remove(plane)
                    # update arrivals and average arrival time
                    self.ENV.score["arrivals"] += 1
                    # self.ENV.score["arrivalsT"] = (
                    #     self.ENV.score["arrivalsT"] * self.ENV.score["arrivals"]
                    #     + plane.timeActive
                    # ) / self.ENV.score["arrivals"] + 1

                    self.new_message(
                        text=f"{plane.callSign} contact ground control at 132.5. Welcome. [+1 POINTS]",
                        bgcolor=self.ENV.GREEN,
                        audio="",
                    )
            # check for safe VOR arrival
            elif (
                x - 10 <= int(plane.x) <= x + 10
                and y - 10 <= int(plane.y) <= y + 10
                and plane.altitude >= self.airspaceInfo["altitudes"]["handOff"]
            ):
                self.activeAirplanes.remove(plane)
                # update departures and average departure time
                self.ENV.score["departures"] += 1
                # self.ENV.score["departuresT"] = (
                #     self.ENV.score["departuresT"] * self.ENV.score["departures"]
                #     + plane.timeActive
                # ) / self.ENV.score["departures"] + 1
                self.new_message(
                    text=f"{plane.callSign} contact air control at 183.4. Goodbye. [+1 POINTS]",
                    bgcolor=self.ENV.GREEN,
                    audio="",
                )
            # check for unsafe airspace exit
            if (
                plane.x < 0
                or plane.x > self.RADAR_WIDTH
                or plane.y < 0
                or plane.y > self.RADAR_HEIGHT
            ):
                self.activeAirplanes.remove(plane)
                self.ENV.score["uncontrolledExits"] -= 1
                self.new_message(
                    text=f"{plane.callSign} uncontrolled exit from airspace. [-1 POINTS]",
                    bgcolor=self.ENV.RED,
                    audio="",
                )

            # check for game winning conditions
            if self.ENV.GAME_MODE == 1 and self.ENV.simTime >= self.ENV.GAME_MODE_GOAL:
                self.ENV.GAME_OVER = True
            if (
                self.ENV.GAME_MODE == 2
                and (self.ENV.score["departures"] + self.ENV.score["arrivals"])
                >= self.ENV.GAME_MODE_GOAL
            ):
                self.ENV.GAME_OVER = True
            if (
                self.ENV.GAME_MODE == 3
                and self.ENV.score["total"] >= self.ENV.GAME_MODE_GOAL
            ):
                self.ENV.GAME_OVER = True

        # process timer
        self.ENV.simTime += dt.now() - self.ENV.simTimeSplit
        self.ENV.simTimeSplit = dt.now()

    def check_proximity(self, plane):
        for other_plane in self.activeAirplanes:
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
                    < self.ENV.MIN_V_SEPARATION * 0.15
                    and dist < self.ENV.MIN_H_SEPARATION * 0.15
                ):
                    self.ENV.collision = True
                    return
                # warning detection
                if (
                    abs(plane.altitude - other_plane.altitude)
                    < self.ENV.MIN_V_SEPARATION
                    and dist < self.ENV.MIN_H_SEPARATION
                    and not plane.isLanding
                    and not other_plane.isLanding
                ):
                    plane.tagColor = self.ENV.RED
                    self.ENV.score["warnings"] = round(
                        self.ENV.score["warnings"] - 0.1, 1
                    )
                    return
                else:
                    plane.tagColor = self.ENV.WHITE
