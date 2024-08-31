import speech_recognition
import os

recog = speech_recognition.Recognizer()


def get_speech():

    with speech_recognition.Microphone() as mic:
        # recog.adjust_for_ambient_noise(mic, duration=0.2)
        audio = recog.listen(mic)

        text = recog.recognize_google(audio)
        text = text.lower()

        if text == "quit":
            quit()

        return text

        print(f"Output: {text}")


def military_alphabet(text):
    with open(
        os.path.join(
            "D:\pythonCode", "Resources", "StaticData", "military_alphabet.txt"
        )
    ) as file:
        ma_index = [i.strip() for i in file.readlines()]

    for word in ma_index:
        text = text.replace(word, word[0])

    print(text)


# for i in range(5):
#     print(get_speech())
