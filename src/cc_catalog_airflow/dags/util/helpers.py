def get_reingestion_day_list_list(*args):
    """
    This method calculates day-shift lists for Provider API workflows.

    The input should be pairs of integers:

    `get_reingestion_day_list_list((x_0, y_0), ..., (x_n, y_n))`

    The return will be a list of lists of integers. The zeroth inner
    list will be a list of integers counting by x_0, of length y_0. The
    first will be a list of integers counting by x_1, of length y_1,
    and in general, the ith list will be a list of integers counting by
    x_i of length y_i. The (i-1)th and ith lists are separated by the
    value x_i.

    For example,
        get_reingestion_day_list_list((1, 2), (2, 3), (3, 2))
    returns
        [[1, 2], [4, 6, 8], [11, 14]]
    """
    return [
        [
            args[i][0] * (j + 1) + sum(arg[0] * arg[1] for arg in args[:i])
            for j in range(args[i][1])
        ]
        for i in range(len(args))
    ]
