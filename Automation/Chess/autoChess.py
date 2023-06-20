import numpy as np
from PIL import Image
import pyautogui
import time, sys
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
from io import BytesIO

# Custom imports
sys.path.append(r"\pythonCode\Resources\Scripts")
from gft_utils import ChromeUtils


class Game:
    def __init__(self) -> None:
        self.color_code = {"W": 0, "B": 1}
        self.chesscom_parameters = {
            "boardElement": (By.ID, "board-layout-chessboard"),
            "left_margin": 30,
            "box_size": 67,
            "sample_coords": (25, 58),
            "sample_color_black": [86, 83, 82, 255],
            "sample_color_white": [248, 248, 248, 255],
            "window_upper_left_corner": (295, 287),
            "window_box_size": 101,
        }

        self.lichess_parameters = {
            "boardElement": (By.XPATH, '//*[@id="main-wrap"]/main/div[1]/div[1]'),
            "left_margin": 4,
            "box_size": 104,
            "sample_coords": (63, 51),
            "sample_color_black": [0, 0, 0, 255],
            "sample_color_white": [255, 255, 255, 255],
            "window_upper_left_corner": (1986, 278),
            "window_box_size": 156,
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

        self.start_lichess()
        self.start_chesscom()

    def button_click(self, wait, type, element):
        button = wait.until(EC.element_to_be_clickable((type, element)))
        button.click()

    def start_lichess(self):
        url = "https://lichess.org/"
        strength = random.randint(3, 6)
        self.webdriver_lichess = ChromeUtils.init_driver(incognito=False)
        self.lichess_parameters.update({"webdriver": self.webdriver_lichess})

        # load tab 1 (we play WHITE)
        self.webdriver_lichess.set_window_position(1300, 0, windowHandle="current")
        self.webdriver_lichess.get(url)
        self.init_lichess(strength=strength, color="W")

        # load tab 2 (we play BLACK)
        self.webdriver_lichess.execute_script("window.open('about:blank','secondtab');")
        self.webdriver_lichess.switch_to.window("secondtab")
        self.webdriver_lichess.get(url)
        self.init_lichess(strength=strength, color="B")

    def init_lichess(self, strength, color):
        wait = WebDriverWait(self.webdriver_lichess, 100)
        # press PLAY WITH THE COMPUTER
        button = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/main/div[1]/div[2]/button[3]")
            )
        )
        button.click()
        # select strength
        self.button_click(
            wait,
            By.XPATH,
            f'//*[@id="modal-wrap"]/div/div/div[3]/div[1]/group/div[{strength}]/label',
        )
        # select color
        self.button_click(
            wait,
            By.XPATH,
            f'//*[@id="modal-wrap"]/div/div/div[4]/button[{"1" if color == "B" else "3"}]',
        )
        # flip board (step 1: open hamburger menu)
        self.button_click(
            wait, By.XPATH, f'//*[@id="main-wrap"]/main/div[1]/rm6/div[1]/button[5]'
        )
        # flip board (step 2: click on FLIP BOARD)
        self.button_click(
            wait,
            By.XPATH,
            f'//*[@id="main-wrap"]/main/div[1]/rm6/div[2]/section[1]/button',
        )

    def start_chesscom(self):
        def play_with_computer():
            # close pop-up (if present)
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(@id, 'placeholder')]")
                )
            )
            self.webdriver_chesscom.find_elements(By.XPATH, "//button")[-2].click()
            time.sleep(5)

            # select "Choose" for player
            button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="board-layout-sidebar"]/div/div[2]/button')
                )
            )
            button.click()
            time.sleep(2)

            # select random color icon
            button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="board-layout-sidebar"]/div/section/div/div[1]/div[2]',
                    )
                )
            )
            button.click()
            time.sleep(2)
            # select "Play" to start game
            button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="board-layout-sidebar"]/div/div[2]/button')
                )
            )
            button.click()

        def play_with_human():
            email = "gabfre@gmail.com"
            password = "$I4#bkDCF)uvURMf"

            input = wait.until(EC.presence_of_element_located((By.ID, "username")))
            ChromeUtils.slow_key_sender(text=email, element=input, return_key=False)
            time.sleep(3)

            input = wait.until(EC.presence_of_element_located((By.ID, "password")))
            ChromeUtils.slow_key_sender(text=password, element=input, return_key=True)
            time.sleep(3)

            url = "https://www.chess.com/play/online/new?action=createLiveChallenge&amp;base=600&amp;timeIncrement=0"
            self.webdriver_chesscom.get(url)

            button = wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="board-layout-sidebar"]/div/div[2]/div/div[1]/div[1]/button',
                    )
                )
            )
            button.click()

            # wait until opponent is live
            print("Log in Complete. Waiting for opponent...")
            txt = 'alt="Opponent"'
            while txt in self.webdriver_chesscom.page_source:
                time.sleep(0.5)

        url = "https://www.chess.com/login_and_go?returnUrl=https://www.chess.com/"
        self.webdriver_chesscom = ChromeUtils.init_driver(incognito=False)
        self.chesscom_parameters.update({"webdriver": self.webdriver_chesscom})
        self.webdriver_chesscom.set_window_position(0, 0, windowHandle="current")
        self.webdriver_chesscom.get(url)
        wait = WebDriverWait(self.webdriver_chesscom, 100)
        play_with_human()

    def opposite(self, color):
        return "B" if color == "W" else "W"

    def sequential_to_coordinates(self, n):
        return (n % 8, n // 8)

    def update_move_timer(self):
        time_elapsed_last_move = time.perf_counter() - self.timer
        if GAME.turn == self.chesscom_parameters:
            self.opp_timer += time_elapsed_last_move
        else:
            self.my_timer += time_elapsed_last_move
        # reset timer since last move
        self.timer = time.perf_counter()


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
        time.sleep(1)

        # check end conditions only if on app
        if check_game_ended_on_chesscom():
            return "QUIT", None
        # get board configuration
        current_board = board_analysis()

        if previous_board != current_board:
            opp_piece_moved = analyze_opp_move(previous_board, current_board)
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
    # insert a 0.5 - 3.0 second delay in chess.com moves
    if GAME.turn == GAME.chesscom_parameters:
        time.sleep(random.randint(1, 6) * 0.5)
    # perform move
    (x0, y0), (x1, y1) = coords
    pyautogui.moveTo(
        GAME.turn["window_upper_left_corner"][0]
        + GAME.turn["window_box_size"] * x0
        + GAME.turn["window_box_size"] * 0.5,
        GAME.turn["window_upper_left_corner"][1]
        + GAME.turn["window_box_size"] * y0
        + GAME.turn["window_box_size"] * 0.5,
        0.4,
        pyautogui.easeOutQuad,
    )
    # check if game has ended before clicking
    if check_game_ended_on_chesscom():
        return True
    pyautogui.mouseDown(button="left")
    pyautogui.moveTo(
        GAME.turn["window_upper_left_corner"][0]
        + GAME.turn["window_box_size"] * x1
        + GAME.turn["window_box_size"] * 0.5,
        GAME.turn["window_upper_left_corner"][1]
        + GAME.turn["window_box_size"] * y1
        + GAME.turn["window_box_size"] * 0.5,
        0.4,
        pyautogui.easeOutQuad,
    )
    pyautogui.mouseUp(button="left")

    # TODO: crowning
    GAME.update_move_timer()
    # print(f"{GAME.my_timer=}  {GAME.opp_timer=}")

    return False

    # check for crowning, always select queen
    if pyautogui.locateOnScreen(
        "crowning_options_black.png"
    ) or pyautogui.locateOnScreen("crowning_options_white.png"):
        pyautogui.moveTo(958, 434, 0.4)
        pyautogui.click()
    # add elapsed time to current turn


def check_game_ended_on_chesscom():
    if pyautogui.locateOnScreen("end_of_game.png"):
        return True


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
    # start timers
    GAME.my_timer, GAME.opp_timer = 0, 0
    GAME.timer = time.perf_counter()

    # determine color we are playing on chesscom (my_color)
    GAME.opp_color = board_analysis(setup=True)
    print("1")
    GAME.my_color = GAME.opposite(GAME.opp_color)
    print("2")
    print(f"{GAME.my_color=}")

    # select lichess window that plays correct color
    GAME.webdriver_lichess.switch_to.window(
        GAME.webdriver_lichess.window_handles[0 if GAME.my_color == "B" else 1]
    )
    print("3")

    # start on chesscom/lichess depending on my color
    GAME.turn = (
        GAME.lichess_parameters.copy()
        if GAME.my_color == "W"
        else GAME.chesscom_parameters.copy()
    )
    print("4")

    time.sleep(1)

    # start looping checking for moves and replicating move in other webpage
    previous_board = None
    while True:
        print("5")
        opp_move, previous_board = wait_for_move(previous_board)
        if opp_move == "QUIT":
            return

        # switch turns
        GAME.turn = (
            GAME.lichess_parameters.copy()
            if GAME.turn == GAME.chesscom_parameters
            else GAME.chesscom_parameters.copy()
        )
        # replicate opponent's move and check if game ended
        if move(coords=opp_move):
            return


def main(games_to_play):
    global GAME
    GAME = Game()

    for game in range(games_to_play):
        print(f"Starting Game {game+1}")
        play_game()
        print("Finished game...")

        # close and reopen lichess
        GAME.webdriver_lichess.quit()
        time.sleep(3)
        GAME.start_lichess()
        # click on "New Game" on chess.com
        time.sleep(10)
        pyautogui.moveTo(1320, 252, 1, pyautogui.easeOutQuad)
        pyautogui.click()
        time.sleep(2)
        # click on "Play"
        pyautogui.moveTo(1382, 490, 1, pyautogui.easeOutQuad)
        pyautogui.click()
        # wait until opponent is live
        print("Waiting for opponent...")
        txt = 'alt="Opponent"'
        while txt in GAME.webdriver_chesscom.page_source:
            time.sleep(0.5)
        # wait a short time for board to reset
        time.sleep(1.5)


# start with indicated number of games in cycle
main(int(sys.argv[1]))
print("End of It All")
