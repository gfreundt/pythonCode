def get_year(vin):
    base_year = 2010 if vin[6].isalpha() else 1980
    offset_options = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "J",
        "K",
        "L",
        "M",
        "N",
        "P",
        "R",
        "S",
        "T",
        "V",
        "W",
        "X",
        "Y",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
    ]
    return base_year + offset_options.index(vin[9])