from tqdm import tqdm


class Boggle:
    def __init__(self):
        self.size = 5
        self.grid, self.translator = self.create_boggle()
        self.full_list = set()
        self.min_letters = 3
        self.max_letters = 9

    def create_boggle(self):
        letter_grid = []
        for _ in range(5):
            t = input()
            letter_grid.append([i for i in t.lower()])
        for i in letter_grid:
            print(" ".join(i))
        # unique characters
        code = 64
        code_grid = []
        translator = {}
        for y in range(self.size):
            line = []
            for x in range(self.size):
                line.append(chr(code))
                translator.update({chr(code): letter_grid[y][x]})
                code += 1
            code_grid.append(line)
        return code_grid, translator

    def create_list(self):
        for y in range(self.size):
            for x in range(self.size):
                build(
                    max_depth=self.max_letters,
                    depth=1,
                    word=self.grid[y][x],
                    start_coord=(y, x),
                )

        translate = lambda word: "".join([self.translator[i] for i in word])
        full_list = set([translate(i) for i in self.full_list])
        with open("boggle.txt", mode="r") as dfile:
            valid_words = [i.strip() for i in dfile.readlines()]
        return [i for i in tqdm(full_list) if i in valid_words]


def build(max_depth, depth, word, start_coord):
    if len(word) >= BOGGLE.min_letters:
        BOGGLE.full_list.add(word)
    if depth >= max_depth:
        return
    # recursion
    y, x = start_coord
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if not (dx == 0 and dy == 0):
                if 0 <= y + dy < 3 and 0 <= x + dx < 3:
                    next_letter = BOGGLE.grid[y + dy][x + dx]
                    if next_letter not in word:
                        start_coord = y + dy, x + dx
                        word += next_letter
                        build(max_depth, depth + 1, word, start_coord)
                        word = word[:-1]


def table(result):
    for length in range(len(result[0]), len(result[-1]) + 1):
        subset = sorted([i for i in result if len(i) == length])
        print(f"Word Length {length}: Total = {len(subset)}")
        print(subset)
    print(f"Total words: {len(result)}")


BOGGLE = Boggle()
result = sorted(BOGGLE.create_list(), key=lambda i: len(i))
table(result)
