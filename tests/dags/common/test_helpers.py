from common.helpers import IngestionInput, get_reingestion_day_list_list


def test_get_reingestion_day_list_list_handles_single_tuple():
    input_list = [
        IngestionInput(2, 3),
    ]
    actual_dll = get_reingestion_day_list_list(input_list)
    expect_dll = [[2, 4, 6]]
    assert actual_dll == expect_dll


def test_get_reingestion_day_list_list_handles_multiple_tuples():
    actual_dll = get_reingestion_day_list_list(
        [IngestionInput(2, 3), IngestionInput(3, 2), IngestionInput(4, 4)]
    )
    expect_dll = [[2, 4, 6], [9, 12], [16, 20, 24, 28]]
    assert actual_dll == expect_dll
