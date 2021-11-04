import common.helpers as helpers


def test_get_reingestion_day_list_list_handles_single_tuple():
    input_tuple = (2, 3)
    actual_dll = helpers.get_reingestion_day_list_list(input_tuple)
    expect_dll = [[2, 4, 6]]
    assert actual_dll == expect_dll


def test_get_reingestion_day_list_list_handles_multiple_tuples():
    actual_dll = helpers.get_reingestion_day_list_list((2, 3), (3, 2), (4, 4))
    expect_dll = [[2, 4, 6], [9, 12], [16, 20, 24, 28]]
    assert actual_dll == expect_dll
