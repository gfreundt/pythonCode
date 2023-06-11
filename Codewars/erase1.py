def ant_bridge(ants, terrain):
    gaps = [len(i) for i in terrain.split("-") if "." in i]
    for gap in gaps:
        ants2 = ants[:gap:]
        ants = ants[gap:] + ants2
    return ants


t = "-------......-------......-----------.--------..------"
ants = "ABCDEFGH"
print(ant_bridge(ants, t))
