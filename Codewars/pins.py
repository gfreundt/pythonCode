def get_pins(observed):
    global code, combos, pins, pin
    code = [int(i) for i in observed]
    combos = {
        1: (1, 2, 4),
        2: (1, 2, 3, 5),
        3: (2, 3, 6),
        4: (1, 4, 5, 7),
        5: (2, 4, 5, 6, 8),
        6: (3, 5, 6, 9),
        7: (4, 7, 8),
        8: (5, 7, 8, 9),
        9: (6, 8, 9),
        0: (8, 0),
    }
    pin = [i for i, _ in enumerate(observed)]
    pins = []
    solve(0)
    return pins


def solve(digit):
    if digit == len(code):
        pins.append("".join(pin))
        return
    for i in combos[code[digit]]:
        pin[digit] = str(i)
        solve(digit + 1)


v = get_pins("369")
c = [
    "339",
    "366",
    "399",
    "658",
    "636",
    "258",
    "268",
    "669",
    "668",
    "266",
    "369",
    "398",
    "256",
    "296",
    "259",
    "368",
    "638",
    "396",
    "238",
    "356",
    "659",
    "639",
    "666",
    "359",
    "336",
    "299",
    "338",
    "696",
    "269",
    "358",
    "656",
    "698",
    "699",
    "298",
    "236",
    "239",
]
print(sorted(v) == sorted(c))
