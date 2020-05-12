def get_reingestion_day_list_list(*args):
    return [
        [
            args[i][0] * (j + 1) + sum(arg[0] * arg[1] for arg in args[:i])
            for j in range(args[i][1])
        ]
        for i in range(len(args))
    ]
