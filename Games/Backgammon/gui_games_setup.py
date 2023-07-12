import os
import pygame


def find_game_path():
    paths = (
        r"D:\Google Drive Backup\Multi-Sync\gui games",
        r"C:\users\gfreu\Google Drive\Multi-Sync\gui games",
        r"C:\pythonCode\chess",
    )
    for path in paths:
        if os.path.exists(path):
            return path


def colors():
    colors = {"BLACK": (0, 0, 0), "WHITE": (255, 255, 255), "BLUE": (0, 0, 255)}
    return colors


def screen(path):
    glogo = os.path.join(path, "_Resources", "Images", "G_logo.png")
    if "D:" in path:
        screen_pos = (2500, 30)
    elif "gfreu" in path:
        screen_pos = (5, 5)
    else:
        screen_pos = (50, 50)
    win_pos = f"{screen_pos[0]},{screen_pos[1]}"
    return glogo, win_pos


def fonts(*args):
    activate_fonts = [
        ["Title", "Arial", 48, "bold", "noitalic"],
        ["SubTitle", "Arial", 24, "bold", "noitalic"],
        ["Text", "Calibri", 16, "nobold", "noitalic"],
    ] + list(args)
    fonts = {
        i[0]: pygame.font.SysFont(
            i[1],
            i[2],
            bold=True if i[3] == "bold" else False,
            italic=True if i[4] == "italic" else False,
        )
        for i in activate_fonts
    }
    return fonts
