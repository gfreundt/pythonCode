from itertools import permutations as perm
from tqdm import tqdm


def next_smaller(n):
    def is_min(n):
        s = [int(i) for i in list(str(n))]
        return all([s[k] < s[k + 1] for k in range(len(str(n)) - 1)])

    # edge cases
    if is_min(n) or len(set(list(str(n)))) < 2:
        return -1

    s = str(n)
    lastq = 2
    while lastq <= len(s):
        print(lastq)
        last = sorted(perm(s[-lastq:]), reverse=True)
        for i in tqdm(last):
            if i[0] == "0":
                continue
            x = int(s[:-lastq] + "".join(i))
            if x < n:
                return x
        lastq += 1
    return -1


print(next_smaller(202233445566))
