# TED Riddles - Autobiographical Numbers
# Python 3.9

import time

def is_autobiog(n):
    m = list(str(n))
    for k, s in enumerate(m):
        if m.count(str(k)) != int(s):
            return False
    return True

def build(digits, construct):
    for n in range(digits):
        construct += str(n)
        if len(construct)<digits:
            build(digits, construct)
        if sum([int(i) for i in construct]) > digits:
            break
        if len(construct) == digits and construct[0] != "0" and is_autobiog(int(construct)):
            print(construct)
        construct = construct[:-1]       

start = time.time()
build(10, "")
print(time.time()-start)