import pytest

from catalog.utilities.media_props_gen.helpers.column_parser import (
    COLUMN_DEFINITIONS,
    Column,
)


@pytest.mark.parametrize(
    "init_args,expected_nullable,expected_str",
    [
        pytest.param(
            {"required": True, "python_type": "URLColumn"},
            False,
            f"{COLUMN_DEFINITIONS['URLColumn']} (`upsert_strategy=newest_non_null, nullable=False, required=True`)",
            id="required=True sets nullable to False",
        ),
        pytest.param(
            {"required": False, "python_type": "StringColumn"},
            True,
            f"{COLUMN_DEFINITIONS['StringColumn']} (`upsert_strategy=newest_non_null, nullable=True, required=False`)",
            id="required=False sets nullable to True",
        ),
        pytest.param(
            {"name": "id", "db_name": "user_id", "python_type": "IntegerColumn"},
            True,
            f'{COLUMN_DEFINITIONS["IntegerColumn"]} '
            f'(`name="id", upsert_strategy=newest_non_null, nullable=True, required=False`)',
            id="name and db_name are different",
        ),
        pytest.param(
            {"name": "id", "python_type": "StringColumn"},
            True,
            f"{COLUMN_DEFINITIONS['StringColumn']} (`upsert_strategy=newest_non_null, nullable=True, required=False`)",
            id="default upsert strategy",
        ),
        pytest.param(
            {
                "name": "genres",
                "python_type": "ArrayColumn",
                "required": False,
                "base_column": "StringColumn",
            },
            True,
            f"{COLUMN_DEFINITIONS['ArrayColumn']} "
            f"(`upsert_strategy=merge_array, base_column=StringColumn, nullable=True, required=False`)",
            id="base_column",
        ),
        pytest.param(
            {
                "name": "audio_set",
                "required": False,
                "python_type": "JSONColumn",
                "upsert_strategy": "merge_jsonb_arrays",
            },
            True,
            f"{COLUMN_DEFINITIONS['JSONColumn']} (`upsert_strategy=merge_jsonb_arrays, nullable=True, required=False`)",
            id="JSONColumn",
        ),
    ],
)
def test_column(init_args, expected_nullable, expected_str):
    column = Column(**init_args)
    assert (
        column.nullable == expected_nullable
    ), "Nullable attribute did not match expected value"
    assert (
        str(column) == expected_str
    ), "__str__ representation did not match expected value"
