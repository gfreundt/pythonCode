""" 
s1 = "my&friend&Paul has heavy hats! &"
s2 = "my friend John has many many friends &"
2:nnnnn/1:aaaa/1:hhh/2:mmm/2:yyy/2:dd/2:ff/2:ii/2:rr/=:ee/=:ss"
2:nnnnn/1:aaaa/1:hhh/2:mmm/2:yyy/2:dd/2:ff/2:ii/2:rr/=:ee/=:ss
"""


def mix(s1, s2):
    d1, d2 = s2d(s1), s2d(s2)
    letters = sorted(set(list(d1.keys()) + list(d2.keys())))

    r = []
    for letter in letters:
        if letter not in d1.keys():
            r.append("2:" + d2[letter] * letter)
        elif letter not in d2.keys():
            r.append("1:" + d1[letter] * letter)
        elif d1[letter] == d2[letter]:
            r.append("=:" + d1[letter] * letter)
        else:
            x = "1" if d1[letter] > d2[letter] else "2"
            r.append(x + ":" + max(d1[letter], d2[letter]) * letter)

    t = []
    for x in range(max([len(i) for i in r]), 3, -1):
        s = sorted([i for i in r if len(i) == x])
        t.append(s)

    t = "/".join([j for i in t for j in i])

    return t

    return sorted(r, key=lambda i: (len(i), i[0]), reverse=True)


def s2d(s):
    s = sorted([i for i in s if i >= "a" and i <= "z"])
    d = {i: s.count(i) for i in s if s.count(i) > 1}
    return d


s1 = "my&friend&Paul has heavy hats! &"
s2 = "my friend John has many many friends &"
print(mix(s1, s2))
