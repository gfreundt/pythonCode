def get_most_profit_from_stock_quotes(quotes):
    profit, stock = 0, 0
    local_max = [
        k for k, _ in enumerate(quotes[1:], start=1) if quotes[k - 1] < quotes[k]
    ]
    if local_max:
        for k, q in enumerate(quotes):
            next_highest = min([i if i > k else 99999 for i in local_max])
            if any([i for i in quotes[k:] if i > q]):
                profit -= q
                stock += 1
            elif q == max(quotes[k:next_highest]):
                profit += q * stock
                stock = 0
    print(gmp(quotes))
    return profit


def gmp(quotes):
    return [max(quotes[i:]) - q for i, q in enumerate(quotes)]


print(get_most_profit_from_stock_quotes([1, 2, 10, 3, 2, 7, 3, 2]))
print(get_most_profit_from_stock_quotes([1, 6, 5, 10, 8, 7]))
print(get_most_profit_from_stock_quotes([6, 5, 4, 3, 2, 1]))
print(get_most_profit_from_stock_quotes([1, 6, 5, 10, 8, 7]))
print(
    get_most_profit_from_stock_quotes(
        [8724, 3165, 8280, 6127, 1947, 8211, 3584, 2478, 8300]
    )
)

"""
([8724, 3165, 8280, 6127, 1947, 8211, 3584, 2478, 8300], 0) should equal 24308


"""
