def fib_digits(n):
    a, b = 0, 1
    for i in range(n - 1):
        a, b = b, a + b
    fib = str(b)
    return sorted(
        [(str(b).count(str(i)), i) for i in range(10) if str(b).count(str(i)) > 0],
        key=lambda i: (i[0], i[1]),
        reverse=True,
    )


print(fib_digits(10000))
