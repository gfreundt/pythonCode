import json
import time
import os
import platform


def load_storyboard(static_directory):
    """Load JSON file that holds all media information"""
    with open(
        os.path.join(static_directory, "json", "storyboard_active_new.json"),
        mode="r",
    ) as json_file:
        storyboard = json.load(json_file)
        return storyboard["active"], storyboard["inactive"]


def main():
    player = vlc.MediaPlayer()
    player.toggle_fullscreen()
    directories = {
        "Windows": r"C:\pythonCode\rollerAds\player\static",
        "Linux": r"/home/pi/pythonCode/rollerAds/player/static",
    }
    static_directory = directories[platform.system()]

    while True:
        # reload storyboard every cycle
        active_media, _ = load_storyboard(static_directory)
        for play_this in active_media:
            media = vlc.Media(
                os.path.join(static_directory, "media", play_this["file_name"])
            )
            player.set_media(media)
            player.play()
            time.sleep(play_this["cycle_duration"])


main()
