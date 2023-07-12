# TODO: castling no check on spaces travelled by king
# TODO: stalemate

from PIL import Image
import sys

import chess_board_score as cbs
import gui_games_setup as setup

import time
from itertools import permutations
import pygame
from pygame.locals import *
import numpy as np
import os
import csv

pygame.init()

# King = 1
# Queen = 2
# Rook = 3
# Bishop = 4
# Knight = 5
# Pawn = 6


class Game:
    def __init__(self):
        self.load_options()
        self.FILE_PATH = setup.find_game_path()
        self.IMAGE_PATH = os.path.join(self.FILE_PATH, "bg", "Images")
        self.COLORS = setup.colors()
        self.SQUARE_SIZE = int(27 * self.scale)
        self.SCREEN_SIZE = (self.SQUARE_SIZE * 8, self.SQUARE_SIZE * 8)
        self.SCREEN_CAPTION = "Chess"
        self.SCREEN_ICON = setup.screen(self.FILE_PATH)
        self.FONTS = setup.fonts(["Small Text", "Calibri", 12, "nobold", "noitalic"])
        self.MOVE_LOG_INDEX = {1: "K", 2: "Q", 3: "R", 4: "B", 5: "N", 6: ""}
        self.load_images()
        self.game_variables()

    def load_options(self):
        load_options = [i.upper() for i in sys.argv]
        scales = (["MICRO", 1], ["MINI", 2], ["NORMAL", 3], ["LARGE", 4])
        for scale in scales:
            if scale[0] in load_options:
                self.scale = scale[1]
                break
            self.scale = 3  # default

    def load_images(self):
        self.squareClearImage = pygame.image.load(
            self.FILE_PATH + r"\Chess\Images\clear_empty.jpg"
        )
        self.squareDarkImage = pygame.image.load(
            self.FILE_PATH + r"\Chess\Images\dark_empty.jpg"
        )
        pcg = {1: "king", 2: "queen", 3: "rook", 4: "bishop", 5: "knight", 6: "pawn"}
        self.pieceImages = {}
        for piece in range(-6, 7):
            if piece != 0:
                img = Image.open(
                    os.path.join(
                        self.IMAGE_PATH,
                        f'{"black" if piece < 0 else "white"}_{pcg[abs(piece)]}.png',
                    )
                ).resize((20 * self.scale, 20 * self.scale), Image.ANTIALIAS)
                self.pieceImages.update(
                    {piece: pygame.image.fromstring(img.tobytes(), img.size, img.mode)}
                )

    def game_variables(self):
        self.activeBoard = np.zeros((8, 8), dtype=int)
        self.en_passant_capture_coords = (0, 0)
        self.castling_left = {
            -1: 1,
            1: 1,
        }  # Key = color, Value = (Left, Right) Side | -1 = Previous Turn Castle Not Available, 0 = Castle Not Available Permanently, 1 = Castle Available
        self.castling_right = {-1: 1, 1: 1}
        self.en_passant = {
            -1: -1,
            1: -1,
        }  # Key = color, Value = -1 Not available | 0-7 column where en passant available
        self.current_turn = 1  # white always starts
        self.in_check = False
        self.fifty_moves_counter = 0
        self.move_log = []


def find_game_path():
    paths = (
        r"D:\Google Drive Backup\Multi-Sync\gui games",
        r"C:\users\gfreu\Google Drive\Multi-Sync\gui games",
    )
    for path in paths:
        if os.path.exists(path):
            return path


def load_init_config():
    board = np.zeros((8, 8), dtype=int)
    with open("chess_config.txt", mode="r") as file:
        for p, x, y in csv.reader(file):
            board[int(x)][int(y)] = int(p)
    return board


def draw_board(moving_piece_coords=(0, 0)):
    # Background
    for x in range(8):
        for y in range(8):
            if (x + y) % 2 == 0:
                screen.blit(
                    game.squareClearImage, (x * game.SQUARE_SIZE, y * game.SQUARE_SIZE)
                )
            else:
                screen.blit(
                    game.squareDarkImage, (x * game.SQUARE_SIZE, y * game.SQUARE_SIZE)
                )
    # Fixed Pieces
    for x in range(8):
        for y in range(8):
            coords = (
                (x * game.SQUARE_SIZE) + 4 * game.scale,
                (y * game.SQUARE_SIZE) + 4 * game.scale,
            )
            image_code = game.activeBoard[(x, y)]
            if image_code != 0:
                screen.blit(game.pieceImages[image_code], coords)
    # Moving Piece
    if moving_piece_coords != (0, 0):
        moving_piece_coords = [i - game.SQUARE_SIZE // 2 for i in moving_piece_coords]
        screen.blit(game.pieceImages[selected_piece], moving_piece_coords)
    pygame.display.update()


def player_action():
    last_mouse_pos = pygame.mouse.get_pos()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return "ESC", None
            if event.type == MOUSEBUTTONDOWN:
                return "MBD", get_square(pygame.mouse.get_pos())
            if event.type == MOUSEBUTTONUP:
                return "MBU", get_square(pygame.mouse.get_pos())
        if pygame.mouse.get_pos() != last_mouse_pos:
            return "MOV", pygame.mouse.get_pos()


def me_in_check():
    game.in_check = False
    all_attacked = []
    for x in range(8):
        for y in range(8):
            piece_reviewed = game.activeBoard[(x, y)]
            if piece_reviewed == 1 * game.current_turn:
                my_king_pos = (x, y)  # find where my king is
            elif piece_reviewed / game.current_turn < 0:
                all_attacked.append(
                    get_destination_squares(piece_reviewed, (x, y), rev=-1)
                )
    if my_king_pos in [item for s in all_attacked for item in s]:
        return True
    return False


def opp_in_check():
    all_attacked = []
    my_king_pos = 0  # to avoid error with if
    for x in range(8):
        for y in range(8):
            piece_reviewed = game.activeBoard[(x, y)]
            if piece_reviewed == -1 * game.current_turn:
                my_king_pos = (x, y)  # find where my king is
            elif piece_reviewed / -game.current_turn < 0:
                all_attacked.append(get_destination_squares(piece_reviewed, (x, y)))
    if (my_king_pos == 0) or (
        my_king_pos in [item for s in all_attacked for item in s]
    ):
        return True
    return False


def get_square(coords):
    return int(coords[0] / game.SQUARE_SIZE), int(coords[1] / game.SQUARE_SIZE)


def long_move(x0, y0, piece, direction):  # queen, rook, bishop
    moves = []
    for a, b in (
        [(-1, 0), (0, -1), (1, 0), (0, 1)]
        if direction == "orthogonal"
        else [(-1, 1), (-1, -1), (1, 1), (1, -1)]
    ):
        x, y = int(a), int(b)
        while True:
            new_coords = (x0 + x, y0 + y)
            if out_of_bounds(new_coords) or (game.activeBoard[new_coords] / piece) > 0:
                break
            elif (game.activeBoard[new_coords] / piece) < 0:
                moves.append(new_coords)
                break
            else:
                moves.append(new_coords)
                x += a
                y += b
    return moves


def knight_move(x0, y0, piece):
    moves = []
    for m in permutations((-2, -1, 1, 2), 2):
        x, y = m[0], m[1]
        if (
            abs(x) - abs(y) != 0
            and not out_of_bounds((x0 + x, y0 + y))
            and (game.activeBoard[(x0 + x, y0 + y)] / piece) <= 0
        ):
            moves.append((x0 + x, y0 + y))
    return moves


def king_move(x0, y0, piece, rev):
    moves = []
    # one square
    for x, y in [(-1, 1), (-1, -1), (1, 1), (1, -1), (0, 1), (0, -1), (1, 0), (-1, 0)]:
        if (
            not out_of_bounds((x0 + x, y0 + y))
            and (game.activeBoard[(x0 + x, y0 + y)] / piece) <= 0
        ):
            moves.append((x0 + x, y0 + y))
    if not game.in_check and rev == 1:  # skip when evaluating positions for check
        # castling long TODO: check for in check or attacked spaces
        line = 0 if game.current_turn < 0 else 7
        if game.castling_left[game.current_turn] and all(
            [game.activeBoard[(x0 - i, line)] == 0 for i in range(2, 4)]
        ):
            moves.append((2, line))
        # castling short TODO: check for in check or attacked spaces
        if game.castling_right[game.current_turn] and all(
            [game.activeBoard[(x0 + i, line)] == 0 for i in range(1, 3)]
        ):
            moves.append((6, line))
    return moves


def pawn_move(x0, y0, piece):
    moves = []
    color = int(piece / abs(piece))
    # one square forward
    new_coords = (x0, y0 - color)
    if game.activeBoard[new_coords] == 0:
        moves.append(new_coords)
        # two squares forward
        new_coords = (x0, y0 - color * 2)
        if ((color == 1 and y0 == 6) or (color == -1 and y0 == 1)) and (
            game.activeBoard[new_coords] == 0
        ):
            moves.append(new_coords)
    # capture
    for cap in (-1, 1):
        new_coords = (x0 + cap, y0 - color)
        if (
            not out_of_bounds(new_coords)
            and -int(game.activeBoard[new_coords] / color) > 0
        ):
            moves.append(new_coords)
    # en passant
    row = 3 if color == 1 else 4
    if game.en_passant[-color] in (x0 - 1, x0 + 1) and y0 == row:
        game.en_passant_capture_coords = (game.en_passant[-color], row - color)
        moves.append(game.en_passant_capture_coords)
    return moves


def out_of_bounds(coords):  # coordinates outside board boundaries
    if (coords[0] < 0) or (coords[0] > 7) or (coords[1] < 0) or (coords[1] > 7):
        return True


def get_destination_squares(piece, square, rev=1, checkmate_test=False):
    x0, y0 = square
    if (int(piece / abs(piece)) == game.current_turn * rev) or checkmate_test:
        if abs(piece) == 1:  # king
            moves = king_move(x0, y0, piece, rev)
        elif abs(piece) == 2:  # queen
            moves = long_move(x0, y0, piece, "orthogonal") + long_move(
                x0, y0, piece, "diagonal"
            )
        elif abs(piece) == 3:  # rook
            moves = long_move(x0, y0, piece, "orthogonal")
        elif abs(piece) == 4:  # bishop
            moves = long_move(x0, y0, piece, "diagonal")
        elif abs(piece) == 5:  # knight
            moves = knight_move(x0, y0, piece)
        elif abs(piece) == 6:  # pawn
            moves = pawn_move(x0, y0, piece)
        return moves


def grid_to_arithmetic(coord):
    x = chr(97 + coord[0])
    y = str(8 - coord[1])
    return x + y


def execute_move(origin, dest, piece, capture=False):

    # print(f"{origin=} {dest=}")

    move_details = {
        "castle": False,
        "from_coord": grid_to_arithmetic(origin),
        "to_coord": grid_to_arithmetic(dest),
        "piece": abs(piece),
        "capture": capture,
        "check": False,
        "promotion": False,
    }
    # castling
    if abs(piece) == 1:
        x, y = dest
        if x == 6 and game.castling_right[game.current_turn]:
            game.activeBoard[dest] = piece
            game.activeBoard[(7, y)], game.activeBoard[(4, y)] = 0, 0
            game.activeBoard[(5, y)] = 3 * game.current_turn
            (
                game.castling_left[game.current_turn],
                game.castling_right[game.current_turn],
            ) = (0, 0)
            move_details["castle"] = "O-O"
            return move_details
        elif x == 2 and game.castling_left[game.current_turn]:
            game.activeBoard[dest] = piece
            game.activeBoard[(0, y)], game.activeBoard[(4, y)] = 0, 0
            game.activeBoard[(3, y)] = 3 * game.current_turn
            (
                game.castling_left[game.current_turn],
                game.castling_right[game.current_turn],
            ) = (0, 0)
            move_details["castle"] = "O-O-O"
            return move_details

    # en passant
    if abs(game.activeBoard[dest]) == 6 and game.en_passant_capture_coords == dest:
        game.activeBoard[(dest[0], origin[1])] = 0

        move_details["capture"] = True
        return move_details

    # regular move or capture + turn off castling if appropriate
    game.activeBoard[dest] = piece
    game.activeBoard[origin] = 0

    if abs(selected_piece) == 1:
        # king move = no castling allowed
        game.castling_left[game.current_turn] = 0
        game.castling_right[game.current_turn] = 0
    elif abs(selected_piece) == 3 and origin[0] == 7:
        # rook move, only right side castling not allowed
        game.castling_right[game.current_turn] = 0
    elif abs(selected_piece) == 3 and origin[0] == 0:
        # rook move, only left side castling not allowed
        game.castling_left[game.current_turn] = 0

    # promotion
    if abs(game.activeBoard[dest]) == 6 and (
        (game.current_turn == 1 and dest[1] == 0)
        or (game.current_turn == -1 and dest[1] == 7)
    ):
        game.activeBoard[dest] = 2 * game.current_turn  # always promote to queen

    # evaluate for en passant activated after move
    if abs(game.activeBoard[dest]) == 6 and abs(origin[1] - dest[1]) == 2:
        game.en_passant[game.current_turn] = origin[0]

    return move_details


def checkmate():
    if opp_in_check():
        for x in range(8):
            for y in range(8):
                piece = game.activeBoard[(x, y)]
                if piece / game.current_turn < 0:
                    alternatives = get_destination_squares(
                        piece, (x, y), checkmate_test=True
                    )
                    for dest in alternatives:
                        previousBoard = game.activeBoard.copy()
                        execute_move((x, y), dest, piece)
                        if not opp_in_check():
                            game.activeBoard = previousBoard.copy()
                            return False
                        else:
                            game.activeBoard = previousBoard.copy()
    else:
        return False
    return True


def stalemate():
    if not opp_in_check():
        for x in range(8):
            for y in range(8):
                piece = game.activeBoard[(x, y)]
                if piece / game.current_turn < 0:
                    alternatives = get_destination_squares(
                        piece, (x, y), checkmate_test=True
                    )
                    for dest in alternatives:
                        previousBoard = game.activeBoard.copy()
                        execute_move((x, y), dest, piece)
                        if not opp_in_check():
                            game.activeBoard = previousBoard.copy()
                            return False
                        else:
                            game.activeBoard = previousBoard.copy()
    else:
        return False
    return True


def insufficient_material():
    flat_board = np.ndarray.flatten(game.activeBoard).tolist()
    # king v king
    if all(i in (-1, 0, 1) for i in flat_board):
        return True
    # king v king + bishop or knight & king v king + 2 knights
    if (
        all(i in (-1, 0, 1, 4) for i in flat_board)
        or all(i in (-1, 0, 1, 5) for i in flat_board)
        or all(i in (-1, 0, 1, -4) for i in flat_board)
        or all(i in (-1, 0, 1, -5) for i in flat_board)
    ) and not (flat_board.count(4) == 2 or flat_board.count(-4) == 2):
        return True
    # king + minor piece v king + minor piece
    if (
        all(i in (-1, 0, 1, 4, -4) for i in flat_board)
        or all(i in (-1, 0, 1, 4, -5) for i in flat_board)
        or all(i in (-1, 0, 1, -4, 5) for i in flat_board)
        or all(i in (-1, 0, 1, -5, 5) for i in flat_board)
    ) and not (
        flat_board.count(4) == 2
        or flat_board.count(-4) == 2
        or flat_board.count(5) == 2
        or flat_board.count(-5) == 2
    ):
        return True


def threefold_repetition():  # TODO: develop
    return False


def move_50_rule():  # Not Working. This part ok, variable adding is broken.
    if game.fifty_moves_counter > 99:
        return True


def end_conditions():
    if checkmate():
        print("checkmate!")
        game.winner = int(game.current_turn)
        game.move_log[-1][-1] = game.move_log[-1][-1].replace("!", "#")
    elif stalemate():
        print("stalemate!")
        game.winner = 0  # draw
    elif insufficient_material():
        game.winner = 0  # draw
        print("insufficient material!")
    elif threefold_repetition():
        game.winner = 0  # draw
        print("threefold repetition!")
    elif move_50_rule():
        game.winner = 0  # draw
        print("50-move rule!")
    else:
        return False
    return True


def log_move(move):
    if not move["castle"]:
        move_text = game.MOVE_LOG_INDEX[move["piece"]]
        # Capture?
        if move["capture"]:
            if move["piece"] == 6:
                move_text += move["from_coord"][0]
            move_text += "x"
        # Add destination coordinates
        move_text += move["to_coord"]
        # Disambiguation
        pass
        # Promotion
        if move["promotion"]:
            move_text += "=Q"
    else:
        move_text = move["castle"]
    # Check / Checkmate
    if move["check"]:
        move_text += "!"
    # Record
    if not game.move_log or len(game.move_log[-1]) == 2:
        game.move_log.append([move_text])
    else:
        game.move_log[-1].append(move_text)


# Game Variables
game = Game()
game.activeBoard = load_init_config()

# Init Screen
os.environ["SDL_VIDEO_WINDOW_POS"] = "50,50"
screen = pygame.display.set_mode(game.SCREEN_SIZE)
pygame.display.set_caption(game.SCREEN_CAPTION)
pygame.display.set_icon(pygame.image.load(game.SCREEN_ICON))

# Main Loop
running = True
while running:
    draw_board()

    # Action 1: Pick up piece
    possible_destinations = []
    selection = False
    while not selection:  # loops while waiting for BEGIN activity from player
        action, square_clicked = player_action()
        if action == "ESC":
            running = False
        elif action == "MBD":
            selected_piece = game.activeBoard[square_clicked]
            if selected_piece:  # clicked on piece, not empty square
                possible_destinations = get_destination_squares(
                    selected_piece, square_clicked
                )
                if (
                    possible_destinations
                ):  # piece was valid to be picked (right color / turn)
                    square_clicked_pick = square_clicked[:]
                    selection = True

    # Action 2: Move piece
    game.activeBoard[square_clicked] = 0  # temporarily erase piece from array
    button_down = True
    while button_down:
        action, moving_piece_coords = player_action()
        if action == "MOV":
            draw_board(moving_piece_coords)
        elif action == "MBU":
            button_down = False

    # Action 3: Drop piece and validate position
    if moving_piece_coords in possible_destinations:
        previousBoard = game.activeBoard.copy()
        capture = True if game.activeBoard[moving_piece_coords] != 0 else False
        game.activeBoard[moving_piece_coords] = selected_piece
        move_details = execute_move(
            square_clicked, moving_piece_coords, selected_piece, capture
        )
        # TODO: increase or reset fifty moves counter

        turn_complete = True
        if me_in_check():
            game.activeBoard = previousBoard.copy()
            game.activeBoard[square_clicked] = selected_piece
            turn_complete = False
        if opp_in_check():
            game.in_check = True
            move_details["check"] = True
        else:
            game.in_check = False
    else:
        game.activeBoard[square_clicked] = selected_piece
        turn_complete = False

    # Check for end of game - if not next turn
    if turn_complete:
        # print(game.fifty_moves_counter)
        log_move(move_details)
        # print(game.move_log)
        if end_conditions():
            print("Moves:", game.move_log)
            running = False
        game.current_turn *= -1
        game.en_passant[game.current_turn] = -1  # clean e.p. opportunity

draw_board()
while True:
    action, moving_piece_coords = player_action()
    if action == "ESC":
        quit()
