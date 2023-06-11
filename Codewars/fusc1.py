"""
1. fusc(0) = 0
2. fusc(1) = 1
3. fusc(2 * n) = fusc(n)
4. fusc(2 * n + 1) = fusc(n) + fusc(n + 1)
"""


def fusc(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n % 2 == 0:
        return fusc(n // 2)
    else:
        return fusc((n - 1) // 2) + fusc(n + 1)


print(fusc(1001))
