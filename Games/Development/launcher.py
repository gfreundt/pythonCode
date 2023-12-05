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

        for k, (opt, module) in enumerate(self.options):
            print(f"{k}> {opt} <")


def main():
    while True:
        sel = int(input("Choose Game:"))
        if not sel:
            return
        exec(f"{MENU.options[sel][1]}.main()")


MENU = Menu()
for i in MENU.options:
    if i[1]:
        exec(f"import {i[1]}")

main()
