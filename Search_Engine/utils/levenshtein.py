import numpy as np


def levenshtein(word1, word2):
    l1 = len(word1) + 1
    l2 = len(word2) + 1
    table = np.zeros((l1, l2))
    table[0][0] = 0
    for i in range(1, l1):
        table[i][0] = i
    for j in range(1, l2):
        table[0][j] = j
    for i in range(1, l1):
        for j in range(1, l2):
            table[i][j] = min(table[i - 1][j - 1] + (1 - (word1[i - 1] == word2[j - 1])),
                              table[i - 1][j] + 1,
                              table[i][j - 1] + 1)
    return int(table[l1 - 1][l2 - 1])
