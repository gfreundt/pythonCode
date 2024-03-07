import random


def get_loops(boxes):
    box = original_box = random.choice(list(boxes.keys()))
    loops = []
    counter = 0
    while True:
        counter += 1
        new_box = boxes[box]
        del boxes[box]
        if not boxes:
            loops.append(counter)
            return loops
        box = new_box
        if box == original_box:
            loops.append(counter)
            counter = 0
            box = original_box = random.choice(list(boxes.keys()))


def create_boxes(n):
    rng = list(range(1, n + 1))
    random.shuffle(rng)
    return {i: j for i, j in zip(range(1, n + 1), rng)}


total = {"over": 0, "under": 0}
for i in range(100000):
    boxes = create_boxes(100)
    loops = get_loops(boxes)
    if [i for i in loops if i > 70]:
        total["over"] += 1
    else:
        total["under"] += 1
    print(total["under"] / (total["over"] + total["under"]), end="\r")
print()
