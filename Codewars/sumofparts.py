def parts_sums(ls):
    print([sum(ls[k:]) for k, _ in enumerate(ls)] + [0])
    r = [sum(ls)]
    for i in ls:
        r.append(r[-1] - i)
    return r


print(parts_sums([744125, 935, 407, 454, 430, 90, 144, 6710213, 889, 810, 2579358]))
