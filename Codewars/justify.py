"""Use spaces to fill in the gaps between words.
Each line should contain as many words as possible.
Use '\n' to separate lines.
Gap between words can't differ by more than one space.
Lines should end with a word not a space.
'\n' is not included in the length of a line.
Large gaps go first, then smaller ones ('Lorem--ipsum--dolor--sit-amet,' (2, 2, 2, 1 spaces)).
Last line should not be justified, use only one space between words.
Last line should not contain '\n'
Strings with one word do not need gaps ('somelongword\n')."""


def justify(text, width):
    split_text = main_split(text, width)
    j = [apply_rules(line, width) + "\n" for line in split_text[:-1]]
    j.append(split_text[-1])
    return "".join(j)


def main_split(text, width):
    split_text = []
    line = 0
    while width < len(text):
        line_text = text[: width + 1]
        while line_text[-1] != " ":
            line_text = line_text[:-1]
        split_text.append(line_text[:-1])
        text = text[len(line_text) :]
        line += 1
    split_text.append(text)
    return split_text


def apply_rules(text, width):
    missing = width - len(text)
    list_of_words = text.split(" ")
    gaps = len(list_of_words) - 1

    if missing * gaps == 0:
        return text

    spaces = [missing // gaps + 2] * (missing % gaps) + [missing // gaps + 1] * (
        gaps - missing % gaps
    )

    d = [i + " " * spaces[k] for k, i in enumerate(list_of_words[:-1])]
    d.append(list_of_words[-1])
    return "".join(d)


text = "The company's leaders since the mid-20th century have been, respectively, W. R. Persons (1954–1973; President), Charles Knight (1973–2000, CEO), and David Farr (2000–2021, CEO). The company's chair of the board have been Charles Knight (1974–2004) and David Farr (since 2004). Emerson is structured into two business units: automation; and commercial and residential."

for width in range(15, 60):
    print(width)
    print(justify(text, width))
