import time


def scroll(text, total_time, screen_size):
    text = " " * (screen_size - 1) + text
    pause = total_time / len(text)
    text += " " * screen_size
    start = time.perf_counter()
    while len(text) > screen_size:
        shown_text = text[:screen_size]
        print(shown_text, end="\r")
        time.sleep(pause)
        text = text[1:]
    print(time.perf_counter() - start)
    print(pause)


text = "We can die"  # at any moment... Our message is dont waste our efforts," Samoilenko said, calling on the Ukrainian government to rely more on continuing fighting against Russian forces than hopes that Moscow can be pacified by negotiations.'
total_time = 10
screen_size = 60


scroll(text, total_time, screen_size)
