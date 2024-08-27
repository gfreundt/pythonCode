import speech_recognition
import pyttsx3

recog = speech_recognition.Recognizer()


def get_speech():

    with speech_recognition.Microphone() as mic:
        # recog.adjust_for_ambient_noise(mic, duration=0.2)
        audio = recog.listen(mic)

        text = recog.recognize_google(audio)
        text = text.lower()

        if text == "quit":
            return

        print(f"Output: {text}")


for i in range(5):
    get_speech()
