def simplify(poly):
    # extract monomials
    if poly[0] not in "+-":
        poly = "+" + poly
    monomials = []
    t = ""
    for p in poly[::-1]:
        if p in "+-":
            monomials.append(p + t[::-1])
            t = ""
        else:
            t += p
    if t:
        monomials.append(t[::-1])
    # order individual letters monomials
    monomials = ["".join(sorted(i)) for i in monomials]
    # load monomial pairs into dictionary and calculate total
    ag = {}
    for mono in monomials:
        try:
            k = 0
            while True:
                if mono[k] >= "a" and mono[k] <= "z":
                    dc = (mono[:k] if len(mono[:k]) > 1 else mono[:k] + "1", mono[k:])
                    break
                else:
                    k += 1
            if dc[1] in ag:
                ag[dc[1]] += dc[0]
            else:
                ag.update({dc[1]: dc[0]})
        except:
            return poly
    ag = {mono: eval(ag[mono]) for mono in ag}
    lag = list(ag)
    # order monomials by increasing number of variables and alphabetical
    lag = sorted(lag, key=lambda i: (len(i), i))
    # put it all together
    s = ""
    for i in lag:
        if ag[i] == -1:
            s += "-" + i
        elif ag[i] == 1:
            s += "+" + i
        elif ag[i] > 1:
            s += "+" + str(ag[i]) + i
        elif ag[i] < 0:
            s += str(ag[i]) + i
    # clean up leading "+" in case it's there
    s = s[1:] if s[0] == "+" else s
    return s


print(simplify("a+4a-5a"))
print(simplify(""))
