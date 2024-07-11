import random
from pygame.locals import *


class UserInput:

    def __init__(self, ATC, ENV, DISP):
        self.ATC = ATC
        self.ENV = ENV
        self.DISP = DISP

    def process_click(self, pos):
        for plane in self.ATC.activeAirplanes:
            if plane.inventoryClickArea.collidepoint(
                pos
            ) or plane.tagClickArea.collidepoint(pos):
                self.ATC.commandText = plane.callSign + " "
                return

    def process_keydown(self, key):
        if key == 27:
            self.DISP.pop_up(action="QUIT", pause=0)
        if self.ATC.commandText in self.ENV.ERRORS:
            self.ATC.commandText = ""
        if 97 <= key <= 122 or 48 <= key <= 57 or key == K_SPACE:  # A - Z + 0 - 9
            self.ATC.commandText += chr(key).upper()
        if key in self.ENV.NUMPAD_KEYS:
            self.ATC.commandText += self.ENV.NUMPAD_KEYS[key]
        elif key == K_BACKSPACE:
            self.ATC.commandText = self.ATC.commandText[:-1]
        elif key in (K_KP_ENTER, K_RETURN):
            self.process_command()
        elif key in (K_LCTRL, K_RCTRL):
            self.ATC.commandText = self.ATC.lastCallSign
        elif key in self.ENV.FUNCTION_KEYS:
            fkey = self.ENV.FUNCTION_KEYS[key]
            if fkey == "F1":
                self.DISP.pop_up(action="HELP", pause=1)
            if fkey == "F2":
                # TODO: move tag to different positions instead of off/on
                self.ENV.tagActive = False if self.ENV.tagActive == True else True
                # pop_up(action="TOGGLE", pause=1)
            if fkey == "F3":
                self.ENV.guidelineActive = (
                    False if self.ENV.guidelineActive == True else True
                )
                # pop_up(action="TOGGLE", pause=1)
            if fkey == "F4":
                self.ENV.audioOn = False if self.ENV.audioOn == True else True
                # pop_up(action="TOGGLE", pause=1)
            if fkey == "F5":
                self.DISP.pop_up(action=None, pause=0)

        elif key == K_TAB:  # testing only
            self.ENV.SPEED = 5 if self.ENV.SPEED == 1 else 1

    def process_command(self):
        error = False
        # if empty command or no planes active
        if not self.ATC.commandText or not self.ATC.activeAirplanes:
            return

        # parse: clean extra spaces
        while "  " in self.ATC.commandText:
            self.ATC.commandText = self.ATC.commandText.replace("  ", " ")
        # TODO: parse: add necessary spaces after valid command

        # extract flight number
        flt, *cmd = self.ATC.commandText.split(" ")
        # check if flight number exists
        plane = [i for i in self.ATC.activeAirplanes if i.callSign == flt]
        if plane:
            plane = plane[0]
            self.ATC.lastCallSign = plane.callSign + " "
        else:
            self.ATC.commandText = ""
            cmd = ""
            error = 3

        # check if format is right (2 or 3 blocks of commands)
        bgcolor_text = self.ENV.BLACK
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
                        plane.altitudeTo,
                        self.ATC.airspaceInfo["altitudes"]["groundLevel"] + 500,
                    )
                    text = f"{plane.callSign} Cleared for Takeoff"
                else:
                    error = 2

            elif cmd[0] == "Q" or cmd[0] == "ABORT":  # abort landing clearance
                if plane.isLanding:
                    plane.isLanding = False
                    plane.speedTo = plane.speedCruise
                    plane.altitudeTo = self.ATC.airspaceInfo["altitudes"]["goAround"]
                    text = f"{plane.callSign} Landing Clearance Cancelled"
                elif plane.ILSIntercept:
                    plane.ILSIntercept = False
                    text = f"{plane.callSign} Landing Clearance Cancelled"
                else:
                    error = 1

            elif cmd[0] == "X":  # only for testing
                plane.isPriority = True
                plane.inventoryColor = self.ENV.RED
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
                        bgcolor_text, text = self.process_expedite(plane, text)
                elif cmd[1].isalpha() and cmd[1] in [
                    i["name"] for i in self.ATC.airspaceInfo["VOR"]
                ]:  # chose VOR
                    VORxy = [
                        (i["x"], i["y"])
                        for i in self.ATC.airspaceInfo["VOR"]
                        if i["name"] == cmd[1]
                    ][0]
                    plane.goToFixed = (VORxy[0], VORxy[1])
                    plane.goToFixedName = cmd[1].strip()
                    text = f"{plane.callSign} Head to {plane.goToFixedName}"
                    if len(cmd) > 2 and cmd[2] in ("R", "L"):
                        plane.turnDirection = cmd[2]
                    if len(cmd) > 2 and cmd[2] == "X":
                        bgcolor_text, text = self.process_expedite(plane, text)
                else:
                    error = 2
            elif cmd[0] == "A" and cmd[1].isdigit():  # change altitude
                new = int(cmd[1])
                if (
                    self.ATC.airspaceInfo["altitudes"]["groundLevel"] + 500
                    <= new * 1000
                    <= plane.altitudeMax
                ):
                    plane.altitudeTo = new * 1000
                    text = f"{plane.callSign} {'Climb' if plane.altitudeTo>plane.altitude else 'Descend'} and Maintain {new*1000:,} feet"
                    if len(cmd) > 2 and cmd[2] == "X":
                        bgcolor_text, text = self.process_expedite(plane, text)
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
                    for s in self.ATC.airspaceInfo["runways"]:
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
                    heading_check = delta_heading <= self.ENV.ILS_HEADING
                    if all([altitude_check, heading_check, plane.isInbound]):
                        plane.ILSIntercept = (
                            selected_runway[0][0][0],
                            selected_runway[0][0][1],
                            selected_runway[0][1],
                        )
                        plane.goToFixedName = f"Runway {cmd[1]} "
                        # new altitude target is runway head altitude
                        text = f"{plane.callSign} Cleared to Intercept ILS for Runway {cmd[1]}"
                        plane.inventoryColor = self.ENV.LIGHT_BLUE
                    else:
                        error = 2
                else:
                    error = 1
            else:
                error = 1
        else:
            error = max(1, error)

        if error:
            self.ATC.commandText = self.ENV.ERRORS[error]
        else:
            self.ATC.new_message(text=text, bgcolor=bgcolor_text, audio=text)
            self.ATC.commandText = ""

    def process_expedite(self, plane, text):
        text += ". Expedite!"
        bgcolor_text = self.ENV.RED
        self.ENV.score["expediteCommands"] = round(
            self.ENV.score["expediteCommands"] - 0.2, 1
        )
        plane.altitudeExpedite = 2
        return bgcolor_text, text
