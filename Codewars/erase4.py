def controller(events):
    pos, moving, result = 0, 0, ""
    for event in events:
        if event == "P":
            moving = (1, 0)[moving]
        elif event == "O":
            moving = -1
        pos += moving
        if pos < 0:
            pos, moving = 0, 0
        elif pos > 5:
            pos, moving = 5, 0
        result += str(pos)
    return result


a = controller("P......P......")  # '0000000000'
# a = controller("P....")  # '12345'
# a = controller("P.P..")  # '12222'
# a = controller("..P...O...")  # '0012343210'

print(a)
