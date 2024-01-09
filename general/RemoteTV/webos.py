import sys, os
import asyncio
import time
from aiowebostv import WebOsClient
import json
import pygame
from PIL import Image
import ssl
import urllib
import requests

# import custom modules
sys.path.append(os.path.join(os.getcwd()[:2], r"\pythonCode", "Resources", "Scripts"))
from gft_utils import pygameUtils

pygame.init()


class Remote:
    def __init__(self) -> None:
        # load general presets
        pygameUtils.__init__(self)
        self.HOST = "192.168.100.4"
        with open(file="webos_keys.json", mode="r") as file:
            self.tv_data = json.loads(file.read())
        self.CLIENT_KEY = self.tv_data["keys"][0]["client_key"]
        self.BUTTONS = self.tv_data["buttons"]

    def handler(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    id = REMOTE.click(pygame.mouse.get_pos())
                    if id:
                        return id
                if event.type == pygame.KEYDOWN:
                    quit()

    def draw_remote(self):
        self.all_buttons = []
        self.button_size = 60
        for button in self.BUTTONS:
            _button = pygame.Surface((self.button_size, self.button_size))
            _button.fill(self.COLORS["BLACK"])
            pygame.draw.rect(
                surface=_button,
                color=self.COLORS["GREEN"],
                rect=(0, 0, self.button_size, self.button_size),
                width=0,
                border_radius=5,
            )
            _img = pygame.transform.scale(
                pygame.image.load(button["image"]),
                (self.button_size - 10, self.button_size - 10),
            )
            _button.blit(source=_img, dest=(5, 5))
            _b = self.MAIN_SURFACE.blit(
                source=_button,
                dest=(
                    button["location"][0] * (self.button_size * 1.2) + 100,
                    button["location"][1] * (self.button_size * 1.2) + 100,
                ),
            )
            self.all_buttons.append(_b)
        pygame.display.flip()

    async def connect(self):
        if not self.client.is_connected():
            await self.client.connect()
            await asyncio.sleep(3)

    async def main(self):
        self.client = WebOsClient(self.HOST, self.CLIENT_KEY)
        await self.connect()
        # apps = await self.client.get_apps()

        # self.apps = json.loads(open("structure.json", "r").read())
        # self.apps = await self.client.get_apps()

        self.draw_remote()

        k = 0
        while True:
            await self.connect()
            cmd = self.handler()
            await self.client.button(cmd)
            await asyncio.sleep(0.5)

        return

        await client.disconnect()

    def click(self, pos):
        for k, b in enumerate(self.all_buttons):
            if b.collidepoint(pos):
                return self.BUTTONS[k]["action"]


REMOTE = Remote()

try:
    asyncio.run(REMOTE.main())


except asyncio.exceptions.TimeoutError:
    print("Could not connect to TV")
"""

BUTTONS=(
    "LEFT",
    "RIGHT",
    "UP",
    "DOWN",
    "RED",
    "GREEN",
    "YELLOW",
    "BLUE",
    "CHANNELUP",
    "CHANNELDOWN",
    "VOLUMEUP",
    "VOLUMEDOWN",
    "PLAY",
    "PAUSE",
    "STOP",
    "REWIND",
    "FASTFORWARD",
    "ASTERISK",
    "BACK",
    "EXIT",
    "ENTER",
    "AMAZON",
    "NETFLIX",
    "3D_MODE",
    "AD",                   # Audio Description toggle
    "ADVANCE_SETTING",
    "ALEXA",                # Amazon Alexa
    "AMAZON",               # Amazon Prime Video app
    "ASPECT_RATIO",         # Quick Settings Menu - Aspect Ratio
    "CC",                   # Closed Captions
    "DASH",                 # Live TV
    "EMANUAL",              # User Guide
    "EZPIC",                # Pictore mode preset panel
    "EZ_ADJUST",            # EzAdjust Service Menu
    "EYE_Q",                # Energy saving panel
    "GUIDE",
    "HCEC",                 # SIMPLINK toggle
    "HOME",                 # Home Dashboard
    "INFO",                 # Info button
    "IN_START",             # InStart Service Menu
    "INPUT_HUB",            # Home Dashboard
    "IVI",
    "LIST",                 # Live TV
    "LIVE_ZOOM",            # Live Zoom
    "MAGNIFIER_ZOOM",       # Focus Zoom
    "MENU",                 # Quick Settings Menu
    "MUTE",
    "MYAPPS",               # Home Dashboard
    "NETFLIX",              # Netflix app
    "POWER",                # Power button
    "PROGRAM",              # TV Guide
    "QMENU",                # Quick Settings Menu
    "RECENT",               # Home Dashboard - Recent Apps or last app
    "RECLIST",              # Recording list
    "RECORD",
    "SAP",                  # Multi Audio Setting
    "SCREEN_REMOTE",        # More Actions panel
    "SEARCH",
    "SOCCER",               # Sport preset
    "TELETEXT",
    "TEXTOPTION",
    "TIMER",                # Sleep Timer panel
    "TV",
    "TWIN",                 # Twin View
    "UPDOWN",               # Always Ready app
    "USP",                  # Movie, TVshow, app list
    "YANDEX",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9"
)

GET_SERVICES = "api/getServiceList"
SET_MUTE = "audio/setMute"
GET_AUDIO_STATUS = "audio/getStatus"
GET_VOLUME = "audio/getVolume"
SET_VOLUME = "audio/setVolume"
VOLUME_UP = "audio/volumeUp"
VOLUME_DOWN = "audio/volumeDown"
GET_CURRENT_APP_INFO = "com.webos.applicationManager/getForegroundAppInfo"
LAUNCH_APP = "com.webos.applicationManager/launch"
GET_APPS = "com.webos.applicationManager/listLaunchPoints"
GET_APPS_ALL = "com.webos.applicationManager/listApps"
GET_APP_STATUS = "com.webos.service.appstatus/getAppStatus"
SEND_ENTER = "com.webos.service.ime/sendEnterKey"
SEND_DELETE = "com.webos.service.ime/deleteCharacters"
INSERT_TEXT = "com.webos.service.ime/insertText"
SET_3D_ON = "com.webos.service.tv.display/set3DOn"
SET_3D_OFF = "com.webos.service.tv.display/set3DOff"
GET_SOFTWARE_INFO = "com.webos.service.update/getCurrentSWInformation"
MEDIA_PLAY = "media.controls/play"
MEDIA_STOP = "media.controls/stop"
MEDIA_PAUSE = "media.controls/pause"
MEDIA_REWIND = "media.controls/rewind"
MEDIA_FAST_FORWARD = "media.controls/fastForward"
MEDIA_CLOSE = "media.viewer/close"
POWER_OFF = "system/turnOff"
POWER_ON = "system/turnOn"
SHOW_MESSAGE = "system.notifications/createToast"
CLOSE_TOAST = "system.notifications/closeToast"
CREATE_ALERT = "system.notifications/createAlert"
CLOSE_ALERT = "system.notifications/closeAlert"
LAUNCHER_CLOSE = "system.launcher/close"
GET_APP_STATE = "system.launcher/getAppState"
GET_SYSTEM_INFO = "system/getSystemInfo"
LAUNCH = "system.launcher/launch"
OPEN = "system.launcher/open"
GET_SYSTEM_SETTINGS = "settings/getSystemSettings"
TV_CHANNEL_DOWN = "tv/channelDown"
TV_CHANNEL_UP = "tv/channelUp"
GET_TV_CHANNELS = "tv/getChannelList"
GET_CHANNEL_INFO = "tv/getChannelProgramInfo"
GET_CURRENT_CHANNEL = "tv/getCurrentChannel"
GET_INPUTS = "tv/getExternalInputList"
SET_CHANNEL = "tv/openChannel"
SET_INPUT = "tv/switchInput"
TAKE_SCREENSHOT = "tv/executeOneShot"
CLOSE_WEB_APP = "webapp/closeWebApp"
INPUT_SOCKET = "com.webos.service.networkinput/getPointerInputSocket"
CALIBRATION = "externalpq/setExternalPqData"
GET_CALIBRATION = "externalpq/getExternalPqData"
GET_SOUND_OUTPUT = "com.webos.service.apiadapter/audio/getSoundOutput"
CHANGE_SOUND_OUTPUT = "com.webos.service.apiadapter/audio/changeSoundOutput"
GET_POWER_STATE = "com.webos.service.tvpower/power/getPowerState"
TURN_OFF_SCREEN = "com.webos.service.tvpower/power/turnOffScreen"
TURN_ON_SCREEN = "com.webos.service.tvpower/power/turnOnScreen"
TURN_OFF_SCREEN_WO4 = "com.webos.service.tv.power/turnOffScreen"
TURN_ON_SCREEN_WO4 = "com.webos.service.tv.power/turnOnScreen"
GET_CONFIGS = "config/getConfigs"
LIST_DEVICES = "com.webos.service.attachedstoragemanager/listDevices"

# webOS TV internal Luna API endpoints
LUNA_SET_CONFIGS = "com.webos.service.config/setConfigs"
LUNA_SET_SYSTEM_SETTINGS = "com.webos.settingsservice/setSystemSettings"
LUNA_TURN_ON_SCREEN_SAVER = "com.webos.service.tvpower/power/turnOnScreenSaver"
LUNA_REBOOT_TV = "com.webos.service.tvpower/power/reboot"
LUNA_REBOOT_TV_WO4 = "com.webos.service.tv.power/reboot"
LUNA_SHOW_INPUT_PICKER = "com.webos.surfacemanager/showInputPicker"
LUNA_SET_DEVICE_INFO = "com.webos.service.eim/setDeviceInfo"
LUNA_EJECT_DEVICE = "com.webos.service.attachedstoragemanager/ejectDevice"
"""
