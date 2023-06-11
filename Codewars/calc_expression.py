# TODO: fix -(


def calc(expression):
    print("input: ", expression)
    # switch double negatives to addition
    expression = expression.replace("--", "+")
    # identify negatives that are operators and change symbol to "@"
    exp = list(expression)
    for k, s in enumerate(exp):
        if s == "-" and (exp[k + 1] in (" ", "(")) and k > 0:
            exp[k] = "@"
    expression = "".join(exp)
    # print("before", exp)
    # create extra parenthesis to prioritize multiplication and division
    expression = "(" + expression + ")"
    expression = expression.replace("+", ")+(")
    expression = expression.replace("@", ")@(")
    expression = expression.replace("+@", ")@(")
    expression = expression.replace("()", "")
    expression = expression.replace("( )", "")
    print("after", expression)
    exp = list(expression)

    # loop from innermost to outermost parenthesis blocks until no parenthesis left
    while "(" in exp:
        print("".join(exp))
        # create parenthesis priorities list
        all, level = [], 0
        for k, s in enumerate(exp):
            if s == "(":
                level += 1
                all.append((level, k))
            elif s == ")":
                all.append((level, k))
                level -= 1
        # replace highest priority parenthesis block with result
        # print(all)
        highest = max([i[0] for i in all])
        for k, p in enumerate(all):
            if p[0] == highest:
                sub_expression = expression[all[k - 1][1] + 1 : all[k][1]]
        # print(f"{expression=}")
        y = calculate(sub_expression)
        expression = expression.replace("(" + sub_expression + ")", str(y))
        exp = list(expression)
    # evaluate final expression
    # print("final", "".join(exp))
    return calculate(expression)


def calculate(expression):

    # extract numbers
    numbers, n, negative = [], "", False
    for s in expression:
        if s.isdigit() or s == ".":
            if negative:
                n += "-"
            n += s
            negative = False
        elif s == "-":
            negative = True
        else:
            if n:
                numbers.append(n)
                n = ""
            negative = False
    if n:
        numbers.append(n)
    numbers = list(map(float, numbers))
    # extract operators
    operators, n = [], ""
    for s in expression:
        if s in ("+", "@", "/", "*"):
            n += s
        else:
            if n:
                operators.append(n)
                n = ""
            negative = False
    if n:
        operators.append(n)

    print("qq", numbers, operators)
    # evaluate expression

    total = numbers[0]
    for k, operator in enumerate(operators, start=1):
        if operator == "*":
            total *= numbers[k]
        if operator == "/":
            total /= numbers[k]
        if operator == "+":
            total += numbers[k]
        if operator == "@":
            total -= numbers[k]

    # print(total)
    return total


cases = (
    ("-50 - 81 - 78 - 52 + 67 + -67 / -96 / 30", -199.4333333),
    ("-39 / -29 - -63 / -95 * 73 / -86 * 56 / 82", 0),
)


# t = "3+(7+(3+8)+4)+(2+(4+8+(3+6)+8))"
# print(">>>>>>>", calc(t))

# for case in cases:
#     print(f"{case[1]} | {calc(case[0])}")

t = "-7 * -(6 / 3)"
print(">>>>>>>>", calc(t))

t = "-(7) * (-17 + 80 + -(58)) + (100 + ((((54 - -63)))) + -3)"
print(">>>>>>>", calc(t))

"""not working:

input:  -7 * -(6 / 3)  - ERROR
input: -(7) * (-17 + 80 + -(58)) + (100 + -((((54 - -63)))) + -3) - ERROR
input:  17 + 39 + 80 - -28 / 33 / -41 / -82 / -24 = 135.99998948437377
input: -62 * 57 * 51 - 82 - 19 / 67 / 86 / -59 = -180315.99994411075
"""
