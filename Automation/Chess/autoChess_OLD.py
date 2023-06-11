import numpy as np
from PIL import ImageGrab
import pyautogui
import time, os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions


class Game:
    def __init__(self) -> None:
        self.timer = time.perf_counter()
        self.my_timer = 0
        self.opp_timer = 0
        self.color_code = {"W": 0, "B": 1}
        self.app_parameters = {
            "cornerx": 0,
            "cornery": 103,
            "sizex": 108,
            "sizey": 108,
            "offset": 20,
            "img_size": 68,
            "target_coordinates": (30, 54),
            "target_guide": (247, 84),
        }
        self.web_parameters = {
            "cornerx": 569,
            "cornery": 176,
            "sizex": 90,
            "sizey": 90,
            "offset": 18,
            "img_size": 54,
            "target_coordinates": (30, 28),
            "target_guide": (255, 0),
        }
        self.castling_parameters = [
            (0, 3, ((3, 0), (1, 0))),
            (3, 7, ((3, 0), (5, 0))),
            (56, 59, ((3, 7), (1, 7))),
            (59, 63, ((3, 7), (5, 7))),
            (0, 4, ((4, 0), (2, 0))),
            (4, 7, ((4, 0), (6, 0))),
            (56, 60, ((4, 7), (2, 7))),
            (60, 63, ((4, 7), (6, 7))),
        ]
        self.web_url = "https://lichess.org/"
        self.default_board_black_bottom = ["W"] * 16 + ["E"] * 32 + ["B"] * 16
        self.default_board_white_bottom = ["B"] * 16 + ["E"] * 32 + ["W"] * 16
        self.webdriver = self.load_webdriver()

    def load_webdriver(self):
        """Define options for Chromedriver"""
        options = WebDriverOptions()
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--silent")
        options.add_argument("--disable-notifications")
        options.add_argument("--incognito")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        return webdriver.Chrome(
            os.path.join(r"C:\pythonCode", "chromedriver.exe"),
            options=options,
        )

    def web_start(self, strength):
        # minimize app, switch to broswer and open URL
        minimize_app()
        self.webdriver.get(GAME.web_url)
        self.webdriver.maximize_window()
        time.sleep(1)
        # Press PLAY WITH THE COMPUTER
        self.webdriver.find_element(
            "xpath", "/html/body/div/main/div[1]/div[2]/a[3]"
        ).click()
        time.sleep(0.5)
        # select Strength
        pyautogui.click(830 + 37 * (strength - 1), 620)
        time.sleep(0.5)
        # select Color
        pyautogui.click(850 + (220 * GAME.color_code[GAME.my_color]), 770)
        time.sleep(4)
        # flip board
        pyautogui.click(1365, 455)
        time.sleep(0.5)

    def opposite(self, color):
        return "B" if color == "W" else "W"

    def sequential_to_coordinates(self, n):
        return (n % 8, n // 8)

    def update_move_timer(self, turn=None):
        time_elapsed_last_move = time.perf_counter() - self.timer
        if turn == self.app_parameters:
            self.opp_timer += time_elapsed_last_move
        else:
            self.my_timer += time_elapsed_last_move
        # reset timer of last move
        self.timer = time.perf_counter()

        # print(f"my time: {600-self.my_timer:.1f}   opp time: {600-self.opp_timer:.1f}")


def app_start():
    # switch to app
    focus_window("app")
    time.sleep(2)
    # press PLAY ONLINE
    pyautogui.click(pyautogui.locateCenterOnScreen("play_online_icon.png"))
    time.sleep(2)
    # press START
    pyautogui.click(pyautogui.locateCenterOnScreen("start_link.png"))
    time.sleep(2)


def focus_window(interface):
    if interface == "app":
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("dex")
        pyautogui.press("enter")
        time.sleep(1)
        pyautogui.getWindowsWithTitle("Samsung DeX")[0].maximize()
    # elif interface == "web":
    #     minimize_app()
    #     pyautogui.getWindowsWithTitle("Chrome")[0].maximize()
    #     time.sleep(1)
    #     quit()


def minimize_app():
    pyautogui.moveTo(1235, 0)
    time.sleep(1.1)
    pyautogui.click(1235, 55)


def alt_tab(turn):
    if turn == GAME.app_parameters:
        minimize_app()
        return GAME.web_parameters
    else:
        focus_window("app")
        return GAME.app_parameters


def board_analysis(parameters, setup):
    cornerx, cornery = parameters["cornerx"], parameters["cornery"]
    sizex, sizey = parameters["sizex"], parameters["sizey"]
    offset = parameters["offset"]
    board = []
    screenshot = ImageGrab.grab().convert("L")
    for y in range(8):
        for x in range(8):
            img = screenshot.crop(
                (
                    cornerx + sizex * x + offset,
                    cornery + sizey * y + offset,
                    cornerx + sizex * (x + 1) - offset,
                    cornery + sizey * (y + 1) - offset,
                )
            )
            piece = get_piece(
                img, parameters["target_coordinates"], parameters["target_guide"]
            )
            if setup:  # only runs once to determine which color we are playing with
                return piece
            board.append(piece)
    return board


def get_piece(img, target_coordinates, target_guide):
    img_array = np.asarray(img)
    x, y = target_coordinates
    white, black = target_guide
    if img_array[y][x] == black:
        return "B"
    if img_array[y][x] == white:
        return "W"
    else:
        return "E"


def analyze_opp_move(turn, previous_board, current_board):
    if previous_board == current_board:
        return None

    # check for special move: castling
    for c in GAME.castling_parameters:
        if (
            previous_board[c[0]] != "E"
            and previous_board[c[1]] != "E"
            and current_board[c[0]] == "E"
            and current_board[c[1]] == "E"
        ):
            return c[2]

    # compare all 64 squares and determine which two have moved
    coords_from, coords_to = None, None
    color_moving = GAME.opp_color if turn == GAME.web_parameters else GAME.my_color
    color_not_moving = GAME.opposite(color_moving)
    for k in range(64):
        if previous_board[k] != current_board[k] and current_board[k] != color_moving:
            if previous_board[k] == color_not_moving:
                coords_from = GAME.sequential_to_coordinates(k)
            else:
                coords_to = GAME.sequential_to_coordinates(k)
        if coords_from and coords_to:
            return coords_from, coords_to


def move(turn, coords):
    (x0, y0), (x1, y1) = coords
    pyautogui.moveTo(
        turn["cornerx"] + turn["sizex"] * x0 + turn["offset"] * 2,
        turn["cornery"] + turn["sizey"] * y0 + turn["offset"] * 2,
        random.randint(5, 8) / 10 if turn == GAME.app_parameters else 0.5,
        pyautogui.easeOutQuad,
    )
    # check if game has ended before clicking
    if check_game_ended(GAME.opposite(turn)):
        return True
    pyautogui.mouseDown(button="left")
    pyautogui.moveTo(
        turn["cornerx"] + turn["sizex"] * x1 + turn["offset"] * 2,
        turn["cornery"] + turn["sizey"] * y1 + turn["offset"] * 2,
        random.randint(5, 8) / 10 if turn == GAME.app_parameters else 0.5,
        pyautogui.easeOutQuad,
    )
    pyautogui.mouseUp(button="left")
    # get mouse out of board to avoid arrow creating errors
    pyautogui.moveTo(1500, 600, 0.2)
    # check for crowning, always select queen
    if pyautogui.locateOnScreen(
        "crowning_options_black.png"
    ) or pyautogui.locateOnScreen("crowning_options_white.png"):
        pyautogui.moveTo(958, 434, 0.4)
        pyautogui.click()
    # add elapsed time to current turn
    GAME.update_move_timer(turn)

    return False


def check_game_ended(turn):
    if pyautogui.locateCenterOnScreen("game_over_icon.png", grayscale=False):
        return True
    else:
        return False


def print_board(board):
    dashes = "-" * 33 + "\n"
    b = dashes
    for y in range(8):
        line = "|"
        for x in range(8):
            line += " " + board[y * 8 + x] + " |"
        b += line + "\n" + dashes
    print(b)


def wait_for_move(turn, init_board, previous_board):
    # if first move load starting board from defaults
    if init_board:
        previous_board = (
            GAME.default_board_black_bottom
            if GAME.my_color == "B"
            else GAME.default_board_white_bottom
        )

    # loop until there is a change in board (move) or end conditions met
    while True:
        # check end conditions only if on app
        if check_game_ended(turn):
            return "QUIT", None
        # get board configuration
        current_board = board_analysis(turn, setup=False)
        opp_piece_moved = analyze_opp_move(turn, previous_board, current_board)

        if opp_piece_moved:
            # piece has moved, check if move is final
            time.sleep(0.7)
            if current_board == board_analysis(turn, setup=False):
                return opp_piece_moved, current_board


def play_game():
    init_board = True
    previous_board = None
    skip_first_wait = False

    global GAME
    GAME = Game()

    # determine color we are playing (my_color) and opponent's color (opp_color)
    GAME.opp_color = board_analysis(GAME.app_parameters, setup=True)
    GAME.my_color = GAME.opposite(GAME.opp_color)

    # if we are starting black on app, then wait for first move from opponent
    if GAME.my_color == "B":
        opp_move, previous_board = wait_for_move(
            turn=GAME.app_parameters, init_board=True, previous_board=None
        )
        init_board = False
        skip_first_wait = True

    # open browser and start website, select strength and color, flip board, set turn
    GAME.web_start(strength=random.randint(5, 7))
    turn = GAME.web_parameters

    # start looping checking for moves and translating them to the other interface
    while True:
        if not skip_first_wait:
            # wait until other moves or end of game
            opp_move, previous_board = wait_for_move(turn, init_board, previous_board)
            if opp_move == "QUIT":
                print("Detected End of Game")
                return
            init_board = False

            # switch app <--> web
            turn = alt_tab(turn)
            time.sleep(0.5)  # minimum

        # never skip wait again
        skip_first_wait = False

        # replicate opponent's move while checking if game ended
        if move(turn, coords=opp_move):
            return


def main():
    # start online game
    app_start()

    while True:
        play_game()
        GAME.webdriver.quit()
        # play sound, pause and click on "New Game", restart everything
        print("\a")
        time.sleep(10)
        start_time = time.perf_counter()
        while True:
            z = pyautogui.locateCenterOnScreen("new_game_link.png", grayscale=False)
            if z:
                pyautogui.click(z[0], z[1])
                break
            elif time.perf_counter() - start_time > 10:
                print("Stopped. Could not find New Game to click.")
                return


main()
