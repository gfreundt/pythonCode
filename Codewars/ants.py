def ant_bridge(ants, terrain):
    gaps = [len(i) + 2 for i in terrain.split("-") if "." in i]
    for gap in gaps:
        ants = ants[-gap:] + ants[:-gap]
    return ants


ants, terrain = "GFEDCBA", "------....-.---"  # AGFEDCB

v = ant_bridge(ants, terrain)

print(v)
