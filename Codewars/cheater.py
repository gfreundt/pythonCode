import itertools

w = input("Letters: ")
base = [i.upper() for i in w]

with open("english84k_3plus.txt", mode="r", encoding="latin-1") as file:
    low = [i.upper().strip() for i in file.readlines()]

print("DOG" in low)

all = []
for i in range(3, min(6, len(w) + 1)):
    comb = [
        "".join(i) for i in list(itertools.permutations(base, i)) if "".join(i) in low
    ]
    all.append(comb)

for s in all:
    print(len(s[0]), s) if s else ""
