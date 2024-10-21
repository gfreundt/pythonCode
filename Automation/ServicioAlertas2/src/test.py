def h(**kwargs):

    print(kwargs)


def g(**kwargs):

    print(kwargs)
    h(**kwargs)


g(flog=4, naf="per", gft=None)
