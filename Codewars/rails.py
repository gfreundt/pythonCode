def encode_rail_fence_cipher(string, n):
    rail_list = create_rail_list(string, n)

    encoded_list = [[] for _ in range(n)]
    for k, s in zip(rail_list, string):
        encoded_list[k].append(s)

    return "".join(["".join(i) for i in encoded_list])


def decode_rail_fence_cipher(string, n):
    rail_list = create_rail_list(string, n)

    rail_list_count = [rail_list.count(i) for i in range(n)]
    start = 0
    encoded_list = []
    for i in rail_list_count:
        encoded_list.append(string[start : start + i])
        start += i
    decoded_string = ""
    for k, s in zip(rail_list, string):
        decoded_string += encoded_list[k][0]
        encoded_list[k] = encoded_list[k][1:]

    return decoded_string


def create_rail_list(string, n):
    rail_list, c = [], 0
    dir = 1
    p = 0
    while p < len(string):
        rail_list.append(c)
        if c == 0:
            dir = 1
        elif c == n - 1:
            dir = -1
        c += dir
        p += 1

    return rail_list


a = decode_rail_fence_cipher("WECRLTEERDSOEEFEAOCAIVDEN", 3)

print(a)
