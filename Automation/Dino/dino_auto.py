import keyboard
import time
import sys
import pyautogui as pyag
import threading
import uuid


class Dino:
    def __init__(self) -> None:
        self.speed = 0
        self.jumps = 0
        self.WHITE = [255, 255, 255]
        self.BLACK = (83, 83, 83)
        self.XJUMP = 2500 + 260 + self.speed * 5
        self.YJUMP = 593
        self.XCAL = 3800
        self.YCAL = 610
        self.XGOVER0 = 3060
        self.YGOVER0 = 410
        self.XGOVER1 = 3148
        self.YGOVER1 = 410
        self.previous_speed = 0

    def check_for_jump(self):
        test = [
            pyag.pixel(x, self.YJUMP) == self.BLACK
            for x in range(self.XJUMP - 7, self.XJUMP + 2, 2)
        ]
        if any(test):
            keyboard.press_and_release("space")
            self.jumps += 1
            time.sleep(0.1)
        if self.jumps == 12:
            self.jump = 0
            self.speed += 1

    def calibrate_speed(self):
        while True:
            time.sleep(1)
            if pyag.pixel(self.XCAL, self.YCAL) == self.BLACK:
                start = time.perf_counter()
                while True:
                    if pyag.pixel(self.XCAL - 400, self.YCAL) == self.BLACK:
                        # print("SPEED MEASURED")
                        end = time.perf_counter()
                        if self.is_real(end - start):
                            self.previous_speed = end - start
                            return "INSERT NEW SPEED HERE"
                        time.sleep(0.5)
                        break

    def is_real(self, new_speed):
        # first time only calibration
        if self.previous_speed == 0:
            self.previous_speed = new_speed
            return
        # measure differences and determine if real speed change
        # print(new_speed, self.previous_speed, "ratio=", new_speed / self.previous_speed)
        if 0.6 < new_speed / self.previous_speed < 0.9:
            return True

    def game_over(self):
        if (
            pyag.pixel(self.XGOVER0, self.YGOVER0) == self.BLACK
            and pyag.pixel(self.XGOVER1, self.YGOVER1) == self.BLACK
        ):
            return True


def thread_speed_calibration():
    while True:
        speed = DINO.calibrate_speed()
        print("Speed Change")
        time.sleep(5)


def thread_game_over(max_loops):
    loops = 0
    while True:
        if loops > max_loops:
            quit()
        if DINO.game_over():
            loops += 1
            print("Game Over - Restaring")
            pyag.screenshot(
                f"score_{str(uuid.uuid4())[:8]}.png",
                region=(3677, 317, 140, 40),
            )
            time.sleep(2)
            keyboard.press_and_release("space")
        time.sleep(9)


def thread_jumping():
    while True:
        DINO.check_for_jump()


def thread_control(max_lapse):
    init = time.perf_counter()
    while True:
        lapse = time.perf_counter() - init
        # print(f"{lapse:.0f}")
        if lapse > max_lapse:
            quit()
        time.sleep(5)


DINO = Dino()
max_loops = int(sys.argv[1]) if len(sys.argv) > 1 else 3
t0 = threading.Thread(target=thread_game_over, args=(max_loops,))
t1 = threading.Thread(target=thread_jumping, args=(), daemon=True)
# t2 = threading.Thread(target=thread_control, args=(program_time,))
t0.start()
t1.start()
# t2.start()
