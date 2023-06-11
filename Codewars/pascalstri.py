def generate_diagonal(n, l):
    triangle = [[1]]
    for _ in range(n + l - 1):
        triangle = gen_next_level(triangle)
    response = [i[n] for i in triangle if len(i) > n]
    return response


def gen_next_level(triangle):
    current_level = triangle[-1]
    new_level = (
        [1]
        + [i + current_level[k] for k, i in enumerate(current_level[:-1], start=1)]
        + [1]
    )
    triangle.append(new_level)
    return triangle


a = generate_diagonal(3, 7)

print(a)
