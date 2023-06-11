import numpy as np
from PIL import ImageGrab, Image
import pyautogui
import time, sys
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as WebDriverOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import base64
from io import BytesIO


class Game:
    def __init__(self) -> None:
        self.timer = time.perf_counter()
        self.my_timer = 0
        self.opp_timer = 0
        self.color_code = {"W": 0, "B": 1}
        self.chesscom_parameters = {
            "boardElement": (By.ID, "board-layout-chessboard"),
            "left_margin": 30,
            "box_size": 67,
            "sample_coords": (25, 58),
            "sample_color_black": [86, 83, 82, 255],
            "sample_color_white": [248, 248, 248, 255],
        }

        self.lichess_parameters = {
            "boardElement": (By.ID, "main-wrap"),
            "left_margin": 15,
            "box_size": 104,
            "sample_coords": (65, 51),
            "sample_color_black": [0, 0, 0, 255],
            "sample_color_white": [255, 255, 255, 255],
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

        self.default_board_black_bottom = ["W"] * 16 + ["E"] * 32 + ["B"] * 16
        self.default_board_white_bottom = ["B"] * 16 + ["E"] * 32 + ["W"] * 16
        self.turn = None

    def load_webdriver(self):
        """Define options for Chromedriver"""
        options = WebDriverOptions()
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--silent")
        options.add_argument("--disable-notifications")
        options.add_argument("--incognito")
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        return webdriver.Chrome(
            service=Service("C:\pythonCode\chromedriver.exe"), options=options
        )

    def start_lichess(self):
        url = "https://lichess.org/"
        strength = random.randint(2, 7)
        self.webdriver0 = self.load_webdriver()
        self.lichess_parameters.update({"webdriver": self.webdriver0})

        # load tab 1 (we play WHITE)
        self.webdriver0.set_window_position(1300, 0, windowHandle="current")
        self.webdriver0.get(url)
        self.init_lichess(strength=strength, color="W")

        # load tab 2 (we play BLACK)
        self.webdriver0.execute_script("window.open('about:blank','secondtab');")
        self.webdriver0.switch_to.window("secondtab")
        self.webdriver0.get(url)
        self.init_lichess(strength=strength, color="B")

    def init_lichess(self, strength, color):
        wait = WebDriverWait(self.webdriver0, 100)
        # press PLAY WITH THE COMPUTER
        button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/main/div[1]/div[2]/button[3]")
            )
        )
        button.click()
        # select strength
        button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f'//*[@id="modal-wrap"]/div/div/div[3]/div[1]/group/div[{strength}]/label',
                )
            )
        )
        button.click()
        # select color
        button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    f'//*[@id="modal-wrap"]/div/div/div[4]/button[{"1" if color == "B" else "3"}]',
                )
            )
        )
        button.click()
        # flip board
        button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, f'//*[@id="main-wrap"]/main/div[1]/rm6/div[1]/button[1]')
            )
        )
        button.click()

    def start_chesscom(self):
        url = "https://chess.com/play/computer"
        self.webdriver1 = self.load_webdriver()
        self.chesscom_parameters.update({"webdriver": self.webdriver1})
        self.webdriver1.set_window_position(0, 0, windowHandle="current")
        self.webdriver1.get(url)
        wait = WebDriverWait(self.webdriver1, 100)

        # Play with Computer (for now)

        # close pop-up (if present)
        wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[contains(@id, 'placeholder')]"))
        )
        self.webdriver1.find_elements(By.XPATH, "//button")[-2].click()
        time.sleep(10)

        # select "Choose" for player
        button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="board-layout-sidebar"]/div/div[2]/button')
            )
        )
        button.click()
        time.sleep(5)
        # select "Play" to start game
        button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="board-layout-sidebar"]/div/div[2]/button')
            )
        )
        button.click()

    def opposite(self, color):
        return "B" if color == "W" else "W"

    def sequential_to_coordinates(self, n):
        return (n % 8, n // 8)

    def update_move_timer(self):
        time_elapsed_last_move = time.perf_counter() - self.timer
        if GAME.turn == self.app_parameters:
            self.opp_timer += time_elapsed_last_move
        else:
            self.my_timer += time_elapsed_last_move
        # reset timer of last move
        self.timer = time.perf_counter()

        # print(f"my time: {600-self.my_timer:.1f}   opp time: {600-self.opp_timer:.1f}")


def stamp_on_screen(parameters):
    s = np.asarray(ImageGrab.grab())
    y = parameters["stamp"]["y"]
    x = parameters["stamp"]["x"]

    f = str(s[y][x : x + 100])
    return f == parameters["stamp"]["reference"]


def board_analysis(setup=False):
    parameters = GAME.chesscom_parameters if setup else GAME.turn
    coords = parameters["sample_coords"]
    webdriver = parameters["webdriver"]
    img = np.array(
        Image.open(
            BytesIO(
                base64.b64decode(
                    webdriver.find_element(
                        parameters["boardElement"][0],
                        parameters["boardElement"][1],
                    ).screenshot_as_base64
                )
            )
        )
    )

    # GAME.webdriver1.find_element(
    #     parameters["boardElement"][0],
    #     parameters["boardElement"][1],
    # ).screenshot("test0.png")

    board = []
    for y in range(8):
        for x in range(8):
            i = img[y * parameters["box_size"] + coords[1]][
                x * parameters["box_size"] + coords[0] + parameters["left_margin"]
            ]
            piece_color = (
                "B"
                if np.array_equal(i, parameters["sample_color_black"])
                else "W"
                if np.array_equal(i, parameters["sample_color_white"])
                else "E"
            )
            if setup:
                return piece_color
            board.append(piece_color)
    return board


def wait_for_move(previous_board):
    # if first move load starting board from defaults
    if not previous_board:
        previous_board = (
            GAME.default_board_black_bottom
            if GAME.my_color == "B"
            else GAME.default_board_white_bottom
        )

    # loop until there is a change in board (move) or end conditions met
    while True:
        print("sleeping 3")
        time.sleep(3)

        # check end conditions only if on app
        # if check_game_ended(turn):
        #     return "QUIT", None
        # get board configuration
        current_board = board_analysis()

        print("previous")
        print_board(previous_board)
        print("current")
        print_board(current_board)

        if previous_board != current_board:
            print("change")
            opp_piece_moved = analyze_opp_move(previous_board, current_board)
            print(opp_piece_moved)
            # wait and check if move is final
            if opp_piece_moved:
                time.sleep(0.5)
                if current_board == board_analysis():
                    return opp_piece_moved, current_board


def analyze_opp_move(previous_board, current_board):
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
    color_moving = (
        GAME.opp_color if GAME.turn == GAME.lichess_parameters else GAME.my_color
    )
    color_not_moving = GAME.opposite(color_moving)
    for k in range(64):
        if previous_board[k] != current_board[k] and current_board[k] != color_moving:
            if previous_board[k] == color_not_moving:
                coords_from = GAME.sequential_to_coordinates(k)
            else:
                coords_to = GAME.sequential_to_coordinates(k)
        if coords_from and coords_to:
            return coords_from, coords_to


def move(coords):
    """
    //*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container/cg-board/square[1]
    //*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container/cg-board/square[2]
    //*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container/cg-board/piece[1]
    //*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container/cg-board/piece[2]

    //*[@id="main-wrap"]/main/div[1]/div[1]/div/cg-container/cg-board/piece[1]

    <square class="last-move" style="transform: translate(134.667px, 404px);"></square>
    """

    (x0, y0), (x1, y1) = coords
    pyautogui.moveTo(
        GAME.turn["cornerx"] + GAME.turn["sizex"] * x0 + GAME.turn["offset"] * 2,
        GAME.turn["cornery"] + GAME.turn["sizey"] * y0 + GAME.turn["offset"] * 2,
        0.2,
        pyautogui.easeOutQuad,
    )
    # check if game has ended before clicking
    if check_game_ended():
        return True
    pyautogui.mouseDown(button="left")
    pyautogui.moveTo(
        GAME.turn["cornerx"] + GAME.turn["sizex"] * x1 + GAME.turn["offset"] * 2,
        GAME.turn["cornery"] + GAME.turn["sizey"] * y1 + GAME.turn["offset"] * 2,
        0.2,
        pyautogui.easeOutQuad,
    )
    pyautogui.mouseUp(button="left")
    # get mouse out of board to avoid arrow creating errors
    pyautogui.moveTo(100, 5)
    # check for crowning, always select queen
    if pyautogui.locateOnScreen(
        "crowning_options_black.png"
    ) or pyautogui.locateOnScreen("crowning_options_white.png"):
        pyautogui.moveTo(958, 434, 0.4)
        pyautogui.click()
    # add elapsed time to current turn
    GAME.update_move_timer()

    return False


def check_game_ended():
    return False
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
    b = b.replace("E", " ")
    print(b)


def play_game():
    global GAME
    GAME = Game()

    GAME.start_lichess()
    print("Loading LICHESS complete")

    testing()

    return

    GAME.start_chesscom()
    print("Loading CHESS.COM complete")

    # determine color we are playing on chesscom (my_color)
    GAME.opp_color = board_analysis(setup=True)
    GAME.my_color = GAME.opposite(GAME.opp_color)
    print(f"{GAME.my_color=}")

    # select lichess window that plays correct color
    GAME.webdriver0.switch_to.window(
        GAME.webdriver0.window_handles[0 if GAME.my_color == "B" else 1]
    )

    # start on chesscom/lichess depending on my color
    GAME.turn = (
        GAME.lichess_parameters.copy()
        if GAME.my_color == "W"
        else GAME.chesscom_parameters.copy()
    )

    print("Begin program...")
    time.sleep(1)

    # start looping checking for moves and replicating move in other webpage
    previous_board = None
    while True:
        opp_move, previous_board = wait_for_move(previous_board)

        GAME.turn = (
            GAME.lichess_parameters.copy()
            if GAME.turn == GAME.chesscom_parameters
            else GAME.chesscom_parameters.copy()
        )
        print(f"{opp_move=}")

        """
        if opp_move == "QUIT":
            print("Detected End of Game")
            return
        """
        # replicate opponent's move and check if game ended
        if move(coords=opp_move):
            return


def testing():
    time.sleep(5)
    print("Start")
    a = GAME.webdriver0.find_elements(By.TAG_NAME, "piece")
    for k, i in enumerate(a):
        print(k, i, i.get_attribute("class"))
    print(len(a))
    time.sleep(5)
    a[4].click()
    time.sleep(10)


def main():
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


play_game()
