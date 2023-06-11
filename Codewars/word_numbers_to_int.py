import codewars_test as test


def get_number(string):
    idx = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
        "eleven": 11,
        "twelve": 12,
        "thirteen": 13,
        "fourteen": 14,
        "fifteen": 15,
        "sixteen": 16,
        "seventeen": 17,
        "eighteen": 18,
        "nineteen": 19,
        "twenty": 20,
        "thirty": 30,
        "forty": 40,
        "fifty": 50,
        "sixty": 60,
        "seventy": 70,
        "eighty": 80,
        "ninety": 90,
    }

    if not string:
        return 0

    n = sum([idx[i] for i in string.split("-")])
    return n


def parse_int(string):

    if string == "zero":
        return 0
    elif string == "one million":
        return 10 ** 6

    # eliminate potential "and" in phrase
    string = string.replace(" and ", "-").strip()
    # convert spaces to dashes
    string = string.replace(" ", "-")
    # parse pre and post thousands
    pos = string.find("thousand")
    parsed = [string[: pos - 1], string[pos + 9 :]] if pos > -1 else ["", string]
    # split pre and post hundred for each section
    number = 0
    for section, thousands in zip(parsed, (1000, 1)):
        pos = section.find("hundred")
        parsed2 = (
            [section[: pos - 1], section[pos + 8 :]] if pos > -1 else ["", section]
        )
        for part, hundreds in zip(parsed2, (100, 1)):
            number += get_number(part) * hundreds * thousands
    return number


v = parse_int("two hundred forty-six")
# v1 = parse_int("two hundred and eighty three thousand seven hundred and seventeen")

print(v)
