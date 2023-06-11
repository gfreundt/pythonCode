from string import ascii_lowercase as aLow


def decode(r):
    f = iter([i for i, c in enumerate(r) if c.isalpha()])
    i = next(f)
    n, r = int(r[:i]), r[i:]
    maps = {chr(97 + n * i % 26): c for i, c in enumerate(aLow)}
    return "Impossible to decode" if len(maps) != 26 else "".join(maps[c] for c in r)


def encode(text, num):
    r = []
    for letter in text:
        x = ord(letter) - 97
        c = num * x % 26
        ch = chr(c + 97)
        r.append(ch)
    return str(num) + "".join(r)


# print(decode("1273409kuqhkoynvvknsdwljantzkpnmfgf"))
print(decode("6015ekx"))
# print(decode("5057aan"))

# print(encode("mer", 6015))
