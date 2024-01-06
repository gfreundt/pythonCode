import asyncio
import time
from aiowebostv import WebOsClient

HOST = "192.168.100.4"
CLIENT_KEY = "e5a39c8cc27b57baa83b2cbb5d10e425"


async def main():
    client = WebOsClient(HOST, CLIENT_KEY)
    print(dir(client))

    await client.connect()

    await client.power_off()

    return

    for _ in range(5):
        await client.volume_up()
        print("===")
        time.sleep(1)

    """print(client.client_key)

    apps = await client.get_apps_all()
    for app in apps:
        print(app)"""

    await client.disconnect()


asyncio.run(main())
