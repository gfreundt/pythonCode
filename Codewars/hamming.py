def hamming(n):
    a, b, c = 2, 3, 5
    i = j = k = 0
    hamming = [1] * n
    for num in range(1, n):
        hamming[num] = min(a, b, c)
        if a == hamming[num]:
            i += 1
            a = 2 * hamming[i]
        if b == hamming[num]:
            j += 1
            b = 3 * hamming[j]
        if c == hamming[num]:
            k += 1
            c = 5 * hamming[k]
    return hamming[-1]


search = 5000
print(hamming(search))
