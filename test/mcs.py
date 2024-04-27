def max_common_substring_all_concat(s1, s2, max_only = False):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    maxlen = 0
    maxpos = (-1, -1)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > maxlen:
                    maxlen = dp[i][j]
                    maxpos = (i, j)
            else:
                if max_only:
                    dp[i][j] = 0 # use this to get single mcs only
                else:
                    dp[i][j] = dp[i - 1][j - 1]
    mcs = s1[maxpos[0]-maxlen:maxpos[0]]
    if max_only:
        return mcs
    # print("mcs", mcs, ' maxlen ', maxlen, ' maxpos ', maxpos)
    result = ""

    i, j = m, n
    while i > 0 and j > 0:
        if s1[i - 1] == s2[j - 1]:
            result += s1[i - 1]
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    # print(result)
    return mcs, result[::-1]

s1 = "fqwraofabcdefij174509812375908723495087opqxyk;lk;bananalk"
s2 = "ananaxycdefuvwopquvoipoaisf"

print(max_common_substring_all_concat(s1, s2, True))
