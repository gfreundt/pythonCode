from asyncore import close_all


def brain_luck(code, program_input):
    # parse code to find matching parenthesis pairs and store them in dictionaries
    n = 0
    inventory = []
    pars = [[] for _ in range(code.count("["))]
    for m, c in enumerate(code):
        if c == "[":
            pars[n].append(m)
            inventory.append(n)
            n += 1
        elif c == "]":
            pars[inventory.pop()].append(m)
    open_pars = {pars[k][0]: pars[k][1] for k, _ in enumerate(pars)}
    close_pars = {open_pars[i]: i for i in open_pars}
    # print(open_pars, close_pars)

    # define initial values
    ip, dp = 0, 0
    mem = [0] * 1000
    pinput = list(program_input)
    output = ""

    # loop thru code and execute instructions
    while ip < len(code):

        if code[ip] == ">":
            dp += 1
        elif code[ip] == "<":
            dp -= 1
        elif code[ip] == "+":
            mem[dp] = mem[dp] + 1 if mem[dp] < 255 else 0
        elif code[ip] == "-":
            mem[dp] = mem[dp] - 1 if mem[dp] > 0 else 255
        elif code[ip] == ".":
            output += chr(mem[dp])
        elif code[ip] == ",":
            mem[dp] = ord(pinput.pop(0))
        elif code[ip] == "[":
            if mem[dp] == 0:
                ip = open_pars[ip]
        elif code[ip] == "]":
            if mem[dp] != 0:
                ip = close_pars[ip]
        ip += 1
        # print(f"{ip=} {dp=} {mem=} {output=}")

    return output


v = brain_luck(",[.[-],]", "Codewars" + chr(0))
print(v)
v = brain_luck(",+[-.,+]", "Codewars" + chr(255))
print(v)
v = brain_luck(",>,<[>[->+>+<<]>>[-<<+>>]<<<-]>>.", chr(8) + chr(9))
print(v)  # , ord(v))
v = brain_luck(
    ",>+>>>>++++++++++++++++++++++++++++++++++++++++++++>++++++++++++++++++++++++++++++++<<<<<<[>[>>>>>>+>+<<<<<<<-]>>>>>>>[<<<<<<<+>>>>>>>-]<[>++++++++++[-<-[>>+>+<<<-]>>>[<<<+>>>-]+<[>[-]<[-]]>[<<[>>>+<<<-]>>[-]]<<]>>>[>>+>+<<<-]>>>[<<<+>>>-]+<[>[-]<[-]]>[<<+>>[-]]<<<<<<<]>>>>>[++++++++++++++++++++++++++++++++++++++++++++++++.[-]]++++++++++<[->-<]>++++++++++++++++++++++++++++++++++++++++++++++++.[-]<<<<<<<<<<<<[>>>+>+<<<<-]>>>>[<<<<+>>>>-]<-[>>.>.<<<[-]]<<[>>+>+<<<-]>>>[<<<+>>>-]<<[<+>-]>[<+>-]<<<-]",
    chr(10),
)
