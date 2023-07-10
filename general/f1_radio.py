from pydub import AudioSegment
import winsound
import time


import os, sys

path = os.path.join("D:", r"\pythonCode", "general")

blip = AudioSegment.from_wav(os.path.join(path, "f1_radio_intro.wav"))

audio = AudioSegment.from_wav(os.path.join(path, f"audio{sys.argv[1]}.wav"))

backg = AudioSegment.from_wav(os.path.join(path, "background.wav"))


mix = blip + audio.overlay(backg[500:]) + blip[300:]

mix.export(os.path.join(path, "final.wav"), format="wav")

time.sleep(3)

winsound.PlaySound(os.path.join(path, "final.wav"), winsound.SND_FILENAME)
