def solve(eq: str):
    eq = eq.split("=")
    vart, cont = 0, 0
    for k, side in zip((-1, 1), eq):
        var, con = 0, 0
        args = side.split(" ")
        plus = True
        for i in args:
            if i == "-":
                plus = False
            elif i == "+":
                plus = True
            elif i == "x":
                var = var + 1 * k if plus else var - 1 * k
            elif i.isdigit():
                con = con + int(i) * k if plus else con - int(i) * k
        vart += var
        cont += con
    return -(cont // vart)


s = solve("x + 1 = 9 - 2")
print(s)
