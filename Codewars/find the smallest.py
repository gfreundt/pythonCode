def smallest(n):
    m = str(n)
    digits = [int(i) for i in m]
    swap = min(digits[1:])
    swap_pos = [k for k, i in enumerate(digits) if i == swap]
    results = []
    # regular swap
    for s in swap_pos:
        for k, i in enumerate(digits):
            if swap <= i:
                new = m[:k] + str(swap) + m[k:s] + m[s + 1 :]
                break
        rfrom = min(s, k) if abs(s - k) == 1 else s
        rto = max(s, k) if abs(s - k) == 1 else k
        results.append([int(new), rfrom, rto])
    # force swap of first number
    temp = []
    for k, i in enumerate(digits, start=1):
        rto = k - 1 if k > 1 else 0
        temp.append([int(m[1:k] + str(digits[0]) + m[k:]), 0, rto])
    temp = sorted(temp, key=lambda i: (i[0], i[1], i[2]))
    results.append(temp[0])
    results = sorted(results, key=lambda i: (i[0], i[1], i[2]))
    return results[0]


print(smallest(935855753))

"""

935855753
[393585575, 8, 0] should equal [358557539, 0, 8]

807563703908374457
[80756370398374457, 10, 0] should equal [75637038908374457, 0, 8]

"""
