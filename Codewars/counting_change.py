import itertools


def solve(target, coins, sofar, combos):
    # print(f"{sofar=}")
    for coin in coins:
        print("coin=", coin)
        print("before:", target, coins, sofar, combos)
        sofar.append(coin)
        print("after:", target, coins, sofar, combos)
        _ = input()
        # print("in", sofar)
        if sum(sofar) < target:
            solve(target, coins, sofar, combos)
            sofar = sofar[:-1]
        elif sum(sofar) == target:
            print("*******", sofar)
            combos.append(sofar)
        sofar = sofar[:-1]


def solve2(target, coins):

    return sum(
        [
            len(
                set(
                    [
                        tuple(sorted(i))
                        for i in itertools.product(coins, repeat=n)
                        if sum(i) == target
                    ]
                )
            )
            for n in range(1, target // min(coins) + 1)
        ]
    )

    r = 0
    for n in range(1, target // min(coins) + 1):
        r += len(
            set(
                [
                    tuple(sorted(i))
                    for i in itertools.product(coins, repeat=n)
                    if sum(i) == target
                ]
            )
        )
    return r


def count_change(target, coins):
    print(solve2(target, coins))  # , [], [])


count_change(4, [1, 2])  # => 3
count_change(10, [5, 2, 3])  # => 4
count_change(11, [5, 7])  # => 0
