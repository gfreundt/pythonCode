class Menu:
    def __init__(self):
        self.options = [
            ("QUIT", ""),
            ("Liquids", "liquids"),
            ("Boom", "boom"),
            ("Backgammon", "bg"),
            ("Mastermind", "mastermind"),
            ("Gravity", "gravity"),
        ]

        for k, (opt, _) in enumerate(self.options):
            print(f"{k}> {opt} <")


def main():
    global MENU
    MENU = Menu()
    while True:
        sel = int(input("Choose Game:"))
        if not sel:
            return
        exec(f"import {MENU.options[sel][1]}")
        exec(f"{MENU.options[sel][1]}.main()")


main()
