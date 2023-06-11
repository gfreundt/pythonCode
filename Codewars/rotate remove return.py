def brain_luck(code, program_input):
    p = 0
    mem = [0] * 100
    pinput = list(program_input)
    output = ""

    if code[p] == ">":
        p += 1
    elif code[p] == "<":
        p -= 1
    elif code[p] == "+":
        mem[p] = mem[p] + 1 if p < 255 else 0
        p += 1
    elif code[p] == "-":
        mem[p] = mem[p] - 1 if p > 0 else 255
        p += 1
    elif code[p] == ".":
        output += mem[p]
        p += 1
    elif code[p] == ",":
        mem[p] = pinput.pop(0)
        p += 1
    elif code[p] == "[":
        if mem[p] == 0:
            p = code.find("]", p) + 1
        else:
            p += 1
    elif code[p] == "]":
        if mem[p] == 0:
            p += 1
        else:
            while True:
                p -= 1
                if code[p] == "[":
                    p += 1
                    break


v = brain_luck(",+[-.,+]", "Codewars" + chr(255))
print(v)
