def theLift(self):
    down, up, stops = [], [], []
    for k, floor in enumerate(self.queue):
        for pax in floor:
            if k < pax:
                up.append((k, pax))
            else:
                down.append((k, pax))
            stops.append(k)
            stops.append(pax)
    s = sorted(set(stops)) if up else sorted(set(stops), reverse=True)
    if s[0] != 0:
        s = [0] + s
    if s[-1] != 0:
        s += [0]
    return s


queue = ((), (), (5, 5, 5), (), (), (), ())
queue = ((), (0,), (), (), (2,), (3,), ())
queue = ((), (3,), (4,), (), (5,), (), ())

f = theLift(queue)

print(f)
