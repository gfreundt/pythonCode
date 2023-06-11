from statistics import mean


def hypertensive(patients):
    hypers = []
    for patient in patients:
        meas = [(int(m.split("/")[0]), int(m.split("/")[1])) for m in patient]
        hypers.append(is_hypertense(meas))
    return hypers.count(1)


def is_hypertense(meas):
    d = mean([i[0] for i in meas])
    s = mean([i[1] for i in meas])
    if d >= 140 and len(meas) > 1:
        return 1
    elif s >= 90 and len(meas) > 1:
        return 1
    for m in meas:
        if m[0] >= 180 and m[1] >= 110:
            return 1
    return 0


g = hypertensive(
    [
        ["130/90", "140/94"],
        ["160/110"],
        ["200/120"],
        ["150/94", "140/90", "120/90"],
        ["140/94", "140/90", "120/80"],
    ]
)

print(g)
