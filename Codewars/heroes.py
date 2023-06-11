from copy import deepcopy as copy


def is_possible(database: dict) -> bool:

    anti = [[] for i in range(len(database))]
    for hero in database:
        for i in database[hero]:
            anti[i].append(hero)

    original = [sorted(database[hero]) for hero in database]

    return anti == original

    database = {i: j for i, j in database.items() if len(j) > 0}
    day1, day2 = [], []
    while len(day1) + len(day2) < len(database):
        for hero in database:
            if not (hero in day1 or hero in day2):
                must_be_in_day1 = [i for i in database[hero] if i in day2]
                must_be_in_day2 = [i for i in database[hero] if i in day1]
                if must_be_in_day1 and must_be_in_day2:
                    return False
                elif must_be_in_day1:
                    day1.append(hero)
                elif must_be_in_day2:
                    day2.append(hero)
                else:
                    day1.append(hero)
    return True


def is_possible2(database: dict) -> bool:
    # eliminate heroes that have no enemies
    database = {i: j for i, j in database.items() if len(j) > 0}
    db = copy(database)
    day1, day2 = [], []
    while database:
        # print(day1, day2)
        # take first hero from list and remove it from database
        d, e = next(iter(database.items()))
        day1.append(d)
        day2 += e
        del database[d]
        # loop while there are additions to any day
        change = True
        while change:
            change = False
            for hero in copy(database):
                # print("try", hero)
                must_be_in_day1 = [i for i in db[hero] if i in day2]
                must_be_in_day2 = [i for i in db[hero] if i in day1]
                if not (hero in day1 or hero in day2):
                    change = True
                    if must_be_in_day1 and must_be_in_day2:
                        return False
                    elif must_be_in_day1:
                        day1.append(hero)
                        # day2 += db[hero]
                        del database[hero]
                    elif must_be_in_day2:
                        day2.append(hero)
                        # day1 += db[hero]
                        del database[hero]
                else:
                    del database[hero]
                    if must_be_in_day1 and must_be_in_day2:
                        return False
                    elif must_be_in_day1:
                        day2 += db[hero]
                    elif must_be_in_day2:
                        day1 += db[hero]

                # print(hero, day1, day2, database)

    return True


s = {
    0: [6, 5],
    1: [6],
    2: [7, 8, 4],
    3: [8, 4],
    4: [3, 2],
    5: [9, 8, 7, 0],
    6: [0, 1, 7],
    7: [2, 5, 6],
    8: [2, 3, 5],
    9: [5],
}

print(is_possible(s))
