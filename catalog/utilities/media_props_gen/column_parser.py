import ast
import copy
from pathlib import Path


COLUMNS_PATH = Path(__file__).parents[2] / "dags" / "common" / "storage" / "columns.py"

COLUMNS_URL = "https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py"  # noqa: E501

COLUMN = {
    "python_type": None,
    "name": None,
    "db_name": None,
    "nullable": None,
    "required": False,
    "upsert_strategy": "newest_non_null",
    "base_column": None,
}

COLUMN_PROPS = COLUMN.keys()

CODE = ast.parse(COLUMNS_PATH.read_text())


def format_python_column(
    python_column: dict[str, any],
    python_column_lines: dict[str, tuple[int, int]],
) -> str:
    """
    Format the Python column properties dictionary to a string that can be
    used in the markdown file.
    """
    col_type = python_column.pop("python_type")
    start, end = python_column_lines[col_type]
    python_column_string = f"[{col_type}]({COLUMNS_URL}#L{start}-L{end}) (`"

    col_name = python_column.pop("name")
    column_db_name = python_column.pop("db_name")
    if column_db_name and col_name != column_db_name:
        python_column_string += f'name="{col_name}", '

    python_column_string += ", ".join(
        [f"{k}={v}" for k, v in python_column.items() if v is not None]
    )

    return f"{python_column_string}`)"


def get_python_column_types() -> dict[str, tuple[int, int]]:
    """
    Extract all types of columns with their line numbers for hyperlinks.
    Sample output: `StringColumn: (3, 5)``
    """
    return {
        item.name: (item.lineno, item.end_lineno)
        for item in ast.iter_child_nodes(CODE)
        if isinstance(item, ast.ClassDef) and item.name.endswith("Column")
    }


def parse_col_argument_value(item):
    """
    Return `attr` for Attribute value (upsert strategies), `func.id` for Call value (base_column),
    and `value` for Constant values such as `true`.
    We don't save the List type used for sql_args.
    """
    # Upsert strategy
    if isinstance(item, ast.Attribute) and isinstance(item.value, ast.Name):
        return item.attr
    # Base column
    elif isinstance(item, ast.Call) and isinstance(item.func, ast.Name):
        return item.func.id
    elif isinstance(item, ast.Constant):
        return item.value
    return item.value


def parse_python_columns() -> dict[str, any]:
    """
    Parse columns.py to a dictionary with the column's `db_name` as a key,
    and the string describing Python column as a value.
    Example output:
    "height": "[IntegerColumn](/link/to/column/type/definition/)" +
    "(`name="height", nullable=True, required=False, upsert_strategy=newest_non_null`)"
    """
    python_column_lines = get_python_column_types()

    # Extracts all the assignments of the form `column_name = <Type>Column(...)`
    cols: list[ast.Call] = [
        item.value
        for item in ast.iter_child_nodes(CODE)
        if isinstance(item, ast.Assign)
        and isinstance(item.value, ast.Call)
        and isinstance(item.value.func, ast.Name)
        and item.value.func.id.endswith("Column")
    ]

    columns = {}
    for col in cols:
        parsed_column = copy.copy(COLUMN) | {
            col.arg: parse_col_argument_value(col.value)
            for col in col.keywords
            if col.arg in COLUMN_PROPS
        }
        parsed_column["python_type"] = col.func.id

        # If required is true, then the media item is discarded if the column is null.
        # This mean that the column cannot have `None` as a value.
        if parsed_column["nullable"] is None:
            parsed_column["nullable"] = (
                True
                if parsed_column["required"] is None
                else not parsed_column["required"]
            )
        db_name = parsed_column.get("db_name") or parsed_column["name"]
        columns[db_name] = format_python_column(parsed_column, python_column_lines)

    return columns
