import itertools


def count_change2(money, coins):
    return sum(
        [
            len(
                set(
                    [
                        tuple(sorted(i))
                        for i in itertools.product(coins, repeat=n)
                        if sum(i) == money
                    ]
                )
            )
            for n in range(1, money // min(coins) + 1)
        ]
    )


def count_change(money, coins):
    def rec(money, coins, purse, responses, depth):
        print(f"outside for {purse=} {depth=}")
        # print(money, coins, purse, responses)
        for coin in coins:
            purse.append(coin)
            print(f"in for {coin=}  {purse=} {depth=}")
            total = sum(purse)
            # print(f"{total=}")
            if total < money:
                rec(money, coins, purse, responses, depth + 1)
                purse = purse[:-1]
            elif total == money:
                if sorted(purse) not in responses:
                    responses.append(sorted(purse))
                print("correct", purse)
            purse = purse[:-1]
        purse = purse[:-1]
        return responses

    responses = []
    purse = []
    a = rec(money, coins, purse, responses, depth=1)
    print(a)
    return len(a)


# print(count_change(10, [5, 2, 3]))
print(count_change(4, [1, 2]))
# print(count_change(13, [3, 5]))
