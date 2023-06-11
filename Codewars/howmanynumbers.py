def find_all(sum_dig, digs):

    def increasing_order(num):
        previous = 0
        for n in str(num):
            if int(n) < previous:
                return False
            else:
                previous = int(n)
        return True

    fro, to = int("1"*digs), int("9"*digs) + 1
    valids = []
    for test in range(fro, to):
        if sum([int(i) for i in str(test)]) == sum_dig and increasing_order(test):
            valids.append(test)
    return [len(valids), min(valids), max(valids)] if valids else []

v = find_all(35,6)

print(v)
    