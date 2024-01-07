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
        self.CLIENT_KEY = self.tv_data[0]["client_key"]

    def handler(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    id = REMOTE.click(pygame.mouse.get_pos())
                    if id:
                        return id
                if event.type == pygame.KEYDOWN:
                    quit()

    async def main(self):
        self.client = WebOsClient(self.HOST, self.CLIENT_KEY)
        await self.client.connect()

        apps = await self.client.get_apps()

        # self.apps = json.loads(open("structure.json", "r").read())
        self.apps = await self.client.get_apps()

        self.surfaces = []
        for k, app in enumerate(self.apps):
            _sfc = pygame.Surface((500, 50))
            _sfc.fill(self.COLORS["BLACK"])
            text = self.FONTS["NUN24"].render(
                f"{app['title']}",
                True,
                self.COLORS["WHITE"],
                self.COLORS["BLACK"],
            )
            _sfc.blit(source=text, dest=(75, 15))
            _img = Image.open(
                urllib.request.urlopen(
                    app["icon"], context=ssl._create_unverified_context()
                )
            )
            _img.save(f"temp{k}.png")
            _img = pygame.transform.scale(pygame.image.load(f"temp{k}.png"), (50, 50))
            _sfc.blit(source=_img, dest=(5, 0))
            _rect = self.MAIN_SURFACE.blit(
                _sfc, (100 + 600 * (k // 10), 60 * (k % 10) + 50)
            )
            self.surfaces.append(_rect)

        pygame.display.flip()

        time.sleep(5)

        id = self.handler()
        await self.client.launch_app(id)
        return

        await client.disconnect()

    def click(self, pos):
        for k, b in enumerate(self.surfaces):
            if b.collidepoint(pos):
                return self.apps[k]["id"]


REMOTE = Remote()

try:
    asyncio.run(REMOTE.main())


except asyncio.exceptions.TimeoutError:
    print("Could not connect to TV")
"""

u = "https://images.chesscomfiles.com/uploads/v1/user/42392072.67344cac.50x50o.98cc65401bd3.jpeg"

a = requests.get(u, stream=True).raw
b = Image.open(a)

b.show()
time.sleep(5)
print(a)
"""
