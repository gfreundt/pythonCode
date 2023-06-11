def prime_factors(n):
    factors, test = [], 2
    while n > 1:
        if n % test == 0:  # and isprime(test):
            factors.append(test)
            n = n // test
        else:
            test = 3 if test == 2 else test + 2
    return "".join(
        [
            f"({f})" if factors.count(f) == 1 else f"({f}**{factors.count(f)})"
            for f in sorted(set(factors))
        ]
    )


def isprime(n):
    return True
    if n == 2:
        return True
    for i in range(5, n // 2 + 3):
        if n % i == 0:
            return False
    return True


g = prime_factors(86240)

print(g)
