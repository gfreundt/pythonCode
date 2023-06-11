from PIL import Image
import numpy as np


img = Image.open("test0.png")
imgp = np.asarray(img)
print(imgp.shape)
# print(imgp)

# 3 --> 835
W = [248, 248, 248, 255]
B = [86, 83, 82, 255]

# W = [255, 255, 255, 255]
# B = [0, 0, 0, 255]

leftMargin = 3
boxSize = 67


for y in range(67):
    for x in range(67):
        v1, v2 = [], []
        for j in range(8):
            for i in range(8):
                v1.append(
                    "W" if np.array_equal(imgp[j * 67 + y][i * 67 + x + 30], W) else "@"
                )
                v2.append(
                    "B" if np.array_equal(imgp[j * 67 + y][i * 67 + x + 30], B) else "@"
                )
        if v1.count("W") == 16 and v2.count("B") == 16:
            print(x, y)  # , v1, v2)
"""
lichess:
+ 43 52
+ 66 52
43 53
66 53
44 54
65 54

chesscom:
32 45
32 46
33 46
29 55
30 55
31 55
32 55
33 55
34 55
35 55
36 55
37 55
38 55
39 55
40 55
41 55
42 55
24 56
25 56
26 56
27 56
28 56
29 56
+ 30 56
31 56
32 56
33 56
34 56
35 56
36 56
37 56
38 56
39 56
40 56
41 56
42 56
43 56
44 56
45 56
46 56
47 56
23 57
24 57
25 57
26 57
27 57
28 57
29 57
30 57
31 57
32 57
33 57
34 57
35 57
36 57
37 57
38 57
39 57
40 57
41 57
42 57
43 57
44 57
45 57
46 57
47 57
22 58
23 58
24 58
25 58
26 58
27 58
28 58
29 58
30 58
31 58
32 58
33 58
34 58
35 58
36 58
37 58
38 58
39 58
40 58
41 58
42 58
43 58
44 58
45 58
46 58
47 58
48 58


"""
