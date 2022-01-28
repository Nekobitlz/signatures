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


def serial_matching(values, matching_value):
    for value in values:
        if value < matching_value:
            return False
    return True


def parallel_matching(values, matching_value):
    for value in values:
        if value >= matching_value:
            return True
    return False


def summational_matching(values, matching_value, threshold):
    summary = 0
    for value in values:
        summary += value - matching_value
    return summary >= threshold


def differential_matching(values, matching_value, threshold):
    summary = 0
    for value in values:
        summary += abs(100 - value) - matching_value
    return summary >= threshold
