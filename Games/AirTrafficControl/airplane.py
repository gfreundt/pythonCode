import pygame


class Airplane(pygame.sprite.Sprite):
    def __init__(self, **kw):
        super().__init__()
        self.ENV = kw["ENV"]
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
        self.timeInit = self.ENV.simTime
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
        self.willMissApproach = kw["willMissApproach"]
        self.willDeclareEmergency = kw["willDeclareEmergency"]
        # create pygame entity - airplane box
        self.boxSurface = pygame.Surface((9, 9))
        self.boxSurface.fill(self.ENV.BG)
        pygame.draw.rect(self.boxSurface, self.ENV.WHITE, (0, 0, 8, 8), width=1)
        self.boxPosition = (-10, -10)  # dummy data
        # create pygame entity - airplane tail
        self.tailPosition0 = (0, 0)
        self.tailPosition1 = (0, 0)
        # default tag text color
        self.tagColor = self.ENV.WHITE
        # create pygame entities (dummy data)
        self.tagText0 = self.tagText1 = self.inventoryText = self.ENV.FONT12.render(
            " ",
            True,
            self.ENV.WHITE,
            self.ENV.BG,
        )
        self.tagPosition0 = self.tagPosition1 = self.inventoryPosition = (
            self.x + 20,
            self.y + 20,
        )
        self.tagClickArea = pygame.Rect(0, 0, 0, 0)
        self.inventoryClickArea = pygame.Rect(0, 0, 0, 0)
