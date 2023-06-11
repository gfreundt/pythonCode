import codewars_test as test
from math import log
from random import randint


def brute(m, n):
    s = 0
    for i in range(m, n + 1):
        s += i.bit_count()
    return s


def ones_in_block(digits):
    n = 2 ** digits
    m = 2 ** (digits - 1)
    return n + m * digits


def count_ones(left, right):

    # add all ones in defined block
    start = int(log(left - 1, 2)) + 1
    end = int(log(right + 1, 2))
    blocks = [i for i in range(start, end)]
    ones = sum([ones_in_block(i) for i in blocks])

    # add edges
    if blocks:
        lower_edge = 2 ** blocks[0] - 1
        upper_edge = 2 ** (blocks[-1] + 1)
    else:
        lower_edge = 0
        upper_edge = left

    a = brute(left, lower_edge)
    b = brute(upper_edge, right)

    return a + ones + b


# test.assert_equals(count_ones(12, 29), 51)
a = randint(100, 10000)
b = randint(100, 10000)
v = count_ones(min(a, b), max(a, b))
print("test", v)
print("brute", brute(min(a, b), max(a, b)))
