def assembler_interpreter(program):
    def clean(line):
        # eliminate inline comments
        p = line[1:].find(";")
        line = line[:p] if p > -1 else line
        # reduce multispaces to one space
        while "  " in line:
            line = line.replace("  ", " ")
        return line

    def get_args(program, pos):
        cmd, arg1, arg2 = (program[pos].lstrip() + " @ @").split(" ")[:3]
        if cmd == "msg":
            return cmd, program[pos][4:], " "
        else:
            return cmd, arg1.replace(",", ""), arg2

    def get_labels(program):
        labels = {}
        for pos, line in enumerate(program):
            if ":" in line:
                cmd, _, _ = get_args(program, pos)
                labels[cmd[:-1]] = pos
        return labels

    def compare(pos, cmp1, cmp2):
        cmp1 = result[cmp1] if cmp1.isalpha() else int(cmp1)
        cmp2 = result[cmp2] if cmp2.isalpha() else int(cmp2)
        cmd, arg1, _ = get_args(program, pos)
        if (
            (cmd == "jne" and cmp1 != cmp2)
            or (cmd == "je" and cmp1 == cmp2)
            or (cmd == "jge" and cmp1 >= cmp2)
            or (cmd == "jg" and cmp1 > cmp2)
            or (cmd == "jle" and cmp1 <= cmp2)
            or (cmd == "jl" and cmp1 < cmp2)
        ):
            return labels[arg1]
        else:
            return pos

    def deconstruct_message(arg1):
        text, blocks, include = "", [], False
        for char in arg1:
            if char == "'":
                include = not (include)
            elif char == ",":
                if include:
                    text += char
                else:
                    blocks.append(text)
                    text = ""
            else:
                if include:
                    text += char
                else:
                    text += str(result[char])
        blocks.append(text)
        return "".join(blocks)

    program = [clean(line) for line in program.split("\n") if len(line) > 0]
    labels = get_labels(program)
    pos = 0
    return_pos = []
    output = ""
    result = {" ": ""}

    while pos < len(program):
        cmd, arg1, arg2 = get_args(program, pos)
        if cmd == "mov":
            result[arg1] = int(result[arg2]) if arg2.isalpha() else int(arg2)
        elif cmd == "inc":
            result[arg1] += 1
        elif cmd == "dec":
            result[arg1] -= 1
        elif cmd == "jnz":
            pos += (
                int(arg2) - 1
                if not ((arg1.isalpha() and result[arg1] == 0) or arg1 == "0")
                else 0
            )
        elif cmd == "add":
            result[arg1] += result[arg2] if arg2.isalpha() else int(arg2)
        elif cmd == "sub":
            result[arg1] -= result[arg2] if arg2.isalpha() else int(arg2)
        elif cmd == "mul":
            result[arg1] *= result[arg2] if arg2.isalpha() else int(arg2)
        elif cmd == "div":
            result[arg1] /= result[arg2] if arg2.isalpha() else int(arg2)
            result[arg1] = int(result[arg1])
        elif ":" in cmd:  # label already captured
            pass
        elif cmd == "jmp":
            pos = labels[arg1]
        elif cmd == "cmp":
            pos = compare(pos + 1, arg1, arg2)
        elif cmd == "call":
            return_pos.append(int(pos))
            pos = labels[arg1]
        elif cmd == "ret":
            pos = int(return_pos[-1])
            return_pos = return_pos[:-1]
        elif cmd == "msg":
            output = deconstruct_message(arg1)
        elif cmd == "end":
            return output
        elif ";" in cmd:  # comment ignored
            pass

        else:
            raise Exception("Wrong Command!", cmd)

        pos += 1

    return -1


code = program_factorial = """
mov   a, 5
mov   b, a
mov   c, a
call  proc_fact
call  print
end

proc_fact:
    dec   b
    mul   c, b
    cmp   b, 1
    jne   proc_fact
    ret

print:
    msg   a, '! = ', c, ' if at all, possible' ; output text
    ret
"""


print(assembler_interpreter(code))
