from itertools import combinations_with_replacement as comb
from itertools import permutations as perm
from itertools import product as prod


def rolldice_sum_prob(sum_, dice_amount):
    p = range(1, 7)
    possible = prod(p, repeat=dice_amount)
    n = [i for i in possible if sum(i) == sum_]
    return len(n) / (6 ** dice_amount)


g = rolldice_sum_prob(8, 3)

print(g)
