# takes: str; returns: [ (str, int) ] (Strings in return value are single characters)
def frequencies(s):
    return [(i, s.count(i)) for i in set(s)]


# takes: [ (str, int) ], str; returns: String (with "0" and "1")
def encode(freqs, s):
    if not s:
        return ""
    letter_order = [
        i[1]
        for i in sorted(
            [(i, s.count(i)) for i in set(s)], key=lambda n: n[1], reverse=True
        )
    ]
    encoding_structure = [f"{'1'*(bit_length)}0" for bit_length, _ in enumerate(freqs)]
    encoding_structure[-1] = encoding_structure[-2][:-1] + "1"
    return "".join([i * j for i, j in zip(encoding_structure, letter_order)])


# takes [ [str, int] ], str (with "0" and "1"); returns: str
def decode(freqs, bits):
    return ""


s = "a"
r = encode(frequencies(s), s)

print(r, len(r))
