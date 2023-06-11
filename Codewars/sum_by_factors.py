import codewars_test as test


def pfactors(n):
    factors, divisor = [], 2
    while n > 1:
        while n % divisor == 0:
            factors.append(divisor)
            n /= divisor
        divisor += 1
    return sorted(set(factors))


def sum_for_list(lst):
    factors = []
    for n in lst:
        factors += pfactors(abs(n))
    output = [[f, sum([i for i in lst if i % f == 0])] for f in set(factors)]
    return sorted(output, key=lambda i: i[0])


print(sum_for_list([-29804, -4209, -28265, -72769, -31744]))
# [[2, -61548], [3, -4209], [5, -28265], [23, -4209], [31, -31744], [53, -72769], [61, -4209], [1373, -72769], [5653, -28265], [7451, -29804]]
