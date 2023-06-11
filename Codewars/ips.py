def ips_between(start, end):
    starts = [int(i) for i in start.split(".")]
    ends = [int(i) for i in end.split(".")]
    s0, e0 = 0, 0
    for k, (s, e) in enumerate(zip(starts, ends)):
        s0 += s * 256 ** (3 - k)
        e0 += e * 256 ** (3 - k)
    return e0 - s0


a = ips_between("20.0.0.10", "20.0.1.0")

print(a)
