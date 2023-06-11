def sum_of_squares(n):
    squares, i = [1], 2
    while squares[-1] <= n:
        squares.append(i ** 2)
        i += 1
    squares = squares[:-1]
    units = []
    while True:
        if squares[-1] > n:
            squares.pop(-1)
        else:
            units.append(squares[-1])
            n -= squares[-1]
        if n == 0:
            print(units)
            return len(units)


for a in range(2, 20):
    x = sum_of_squares(a)
    print(f"{a} = {x}")
