# importing vlc module
import vlc, os

# importing time module
import time

pathx = os.path.join(r"\pythonCode", "rollerAds", "player", "static", "media")

# creating a media player object
media_player = vlc.MediaPlayer()
media_player.toggle_fullscreen()

# creating Instance class object
# player = vlc.Instance()

t = time.perf_counter()
for s in os.listdir(pathx):
    print(s)
    media_player.set_media(vlc.Media(os.path.join("static", "media", s)))
    media_player.play()
    time.sleep(10)
print(time.perf_counter() - t)
