def test_correctness(list1, list2):
    lists_len = len(list1)
    if lists_len != len(list2):
        return 0

    correctness_percent = 100
    error_percent = 1 / lists_len * 100

    for i in range(0, lists_len):
        if list1[i] != list2[i]:
            correctness_percent = correctness_percent - error_percent

    return correctness_percent
