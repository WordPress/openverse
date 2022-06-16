from typing import List, NamedTuple


class IngestionInput(NamedTuple):
    day_shift: int
    repeats: int


def get_reingestion_day_list_list(inputs: List[IngestionInput]):
    """
    This method calculates day-shift lists for Provider API workflows.

    The input should be a list of pairs of integers:

    `get_reingestion_day_list_list((x_0, y_0), ..., (x_n, y_n))`

    The return will be a list of lists of integers. The zeroth inner
    list will be a list of integers counting by x_0, of length y_0. The
    first will be a list of integers counting by x_1, of length y_1,
    and in general, the ith list will be a list of integers counting by
    x_i of length y_i. The zeroth list begins counting from 0, and each
    subsequent ith list begins counting at the final value of the (i-1)th
    list.

    For example,
        get_reingestion_day_list_list((1, 2), (2, 3), (3, 2))
    returns
        [[1, 2], [4, 6, 8], [11, 14]]
    """
    # Remove any input pair with 0 repeats
    inputs = [input for input in inputs if input.repeats != 0]

    return [
        [
            inputs[i].day_shift * (j + 1)
            + sum(input.day_shift * input.repeats for input in inputs[:i])
            for j in range(inputs[i].repeats)
        ]
        for i in range(len(inputs))
    ]
