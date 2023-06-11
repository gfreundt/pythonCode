import time

# start = time.time()


def solve(*equations):

    global answer
    answer = []

    terms = [aggregate_terms(break_terms(i)) for i in equations]
    vars = list(set([k for j in [get_unique_variables(i) for i in terms] for k in j]))
    vars = {i: 0 for i in vars if i != ""}

    response = iterate_options(terms, n=150, vars=vars, depth=0, max_depth=len(vars))

    if not response:
        response = iterate_options(
            terms, n=1000, vars=vars, depth=0, max_depth=len(vars)
        )

    return response


def break_terms(equation):
    def split_terms(equation):
        term_split_pos = (
            [0]
            + [k for k, i in enumerate(equation) if i in "+-" and k > 0]
            + [len(equation) + 1]
        )
        terms = [
            equation[term_split_pos[k] : term_split_pos[k + 1]]
            for k in range(0, len(term_split_pos) - 1)
        ]
        terms = [i if ("-" in i or "+" in i) else "+" + i for i in terms]
        return terms

    def invert_signs(terms):
        inverted = []
        for term in terms:
            term = term.replace("+", "@")
            term = term.replace("-", "+")
            term = term.replace("@", "-")
            inverted.append(term)
        return inverted

    def to_dict(term):
        p = 0
        while True and p < len(term):
            if not (term[p].isdigit() or term[p] in "+-"):
                break
            else:
                p += 1
        if p == 1:  # no coefficient (implicit 1)
            term = term[0] + "1" + term[1:]
            p = 2
        return {"coefficient": int(term[:p]), "variable": term[p:]}

    left, right = equation.split("=")
    terms = split_terms(left) + invert_signs(split_terms(right))
    terms = [to_dict(term) for term in terms]

    return terms


def aggregate_terms(term):
    result = []
    for var in get_unique_variables(term):
        agg = sum([i["coefficient"] for i in term if i["variable"] == var])
        result.append({"coefficient": agg, "variable": var})
    return result


def get_unique_variables(terms):
    d = [i["variable"] for i in terms]
    return sorted(list(set(d)))


def iterate_options(terms, n, vars, depth, max_depth):

    if depth >= max_depth:
        return answer

    for next in range(-n, n):
        vars.update({[i for i in vars.keys()][depth]: next})
        if evaluate_for_zero(terms, vars):
            answer.append(vars.copy())
            return answer
        else:
            iterate_options(terms, n, vars, depth + 1, max_depth)

    return answer


def evaluate_for_zero(terms, vars):
    varvals = vars.copy()
    varvals.update({"": 1})
    for term in terms:
        evaluation = 0
        for t in term:
            evaluation += t["coefficient"] * varvals[t["variable"]]
        if evaluation != 0:
            return False
    return True


test = ["2alpha+8beta=4", "-alpha+4beta=14"]
test = ["x=4y", "2x=8y", "x+y=5"]
test = ["x+y=7z-1", "6x+z=-3y", "4y+10z=-8x"]
test = ["2x=4"]

print(solve("x+2y=1", "2x=2-4y"))
# print(solve("2alpha+8beta=4", "-alpha+4beta=14"))

# print(f"Time: {time.time()-start:.4f}")
