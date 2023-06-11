def hydrate(drink_string):
    return f'{sum([int("".join([c for c in i if c.isdigit()])) for i in drink_string.split(",")])} glasses of water'


print(hydrate("1 shot, 5 beers, 2 shots, 1 glass of wine, 1 beer"))
