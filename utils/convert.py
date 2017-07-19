def trits(input):
    trytesTrits = [
        [0, 0, 0],
        [1, 0, 0],
        [-1, 1, 0],
        [0, 1, 0],
        [1, 1, 0],
        [-1, -1, 1],
        [0, -1, 1],
        [1, -1, 1],
        [-1, 0, 1],
        [0, 0, 1],
        [1, 0, 1],
        [-1, 1, 1],
        [0, 1, 1],
        [1, 1, 1],
        [-1, -1, -1],
        [0, -1, -1],
        [1, -1, -1],
        [-1, 0, -1],
        [0, 0, -1],
        [1, 0, -1],
        [-1, 1, -1],
        [0, 1, -1],
        [1, 1, -1],
        [-1, -1, 0],
        [0, -1, 0],
        [1, -1, 0],
        [-1, 0, 0]
    ]

    trytesAlphabet = "9ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    trits = [0] * (len(input) * 3)

    for i in range(0, len(input)):
        index = trytesAlphabet.index(input[i])
        trits[i * 3] = trytesTrits[index][0]
        trits[i * 3 + 1] = trytesTrits[index][1]
        trits[i * 3 + 2] = trytesTrits[index][2]

    return trits