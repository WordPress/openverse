import ast
from pathlib import Path


STORAGE_PATH = Path(__file__).parents[2] / "dags" / "common" / "storage"
COLUMNS_PATH = STORAGE_PATH / "columns.py"

COLUMNS_URL = "https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py"  # noqa: E501


def format_python_column(
    column_db_name: str,
    python_column: dict[str, any],
    python_column_lines: dict[str, tuple[int, int]],
) -> str:
    col_type = python_column.pop("python_type")
    start, end = python_column_lines[col_type]
    python_column_string = f"[{col_type}]({COLUMNS_URL}#L{start}-L{end})("
    col_name = python_column.pop("name")
    if col_name != column_db_name:
        python_column_string += f"name='{col_name}', "
    custom_props = python_column.pop("custom_column_props", None)
    custom_props_string = ""
    if custom_props:
        props_string = ", ".join([f"{k}={v}" for k, v in custom_props.items()])
        custom_props_string = f", {col_type}Props({props_string})"
    python_column_string += ", ".join([f"{k}={v}" for k, v in python_column.items()])
    python_column_string += f"{custom_props_string})"

    return python_column_string


def parse_python_columns() -> dict[str, any]:
    """Get the Python column definitions from the columns.py file."""
    columns = {}
    python_column_lines = get_python_column_types()

    with open(COLUMNS_PATH) as f:
        contents = f.read()
    code = ast.parse(contents)

    for item in ast.iter_child_nodes(code):
        if isinstance(item, ast.Assign):
            column = parse_column_definition(item)
            if not column:
                continue
            db_name = column["db_name"]
            del column["db_name"]
            columns[db_name] = format_python_column(
                db_name, column, python_column_lines
            )

    return columns


def get_python_column_types() -> dict[str, tuple[int, int]]:
    """
    Parse the columns.py file to get the Python column names
    and their line numbers for hyperlinks.
    Sample output: `StringColumn: (3, 5)``
    """
    with open(COLUMNS_PATH) as f:
        file_contents = f.read()
    code = ast.parse(file_contents)
    return {
        item.name: (item.lineno, item.end_lineno)
        for item in ast.iter_child_nodes(code)
        if isinstance(item, ast.ClassDef) and item.name.endswith("Column")
    }


def parse_column_definition(item: ast.Assign) -> dict[str, any] | None:
    column = {
        "python_type": None,
        "name": None,
        "db_name": None,
        "nullable": None,
        "required": False,
        "upsert_strategy": "newest_non_null",
        "custom_column_props": {},
    }
    if hasattr(item.value, "func") and hasattr(item.value.func, "id"):
        column["python_type"] = item.value.func.id

    if hasattr(item.value, "keywords"):
        for kw in item.value.keywords:
            if hasattr(kw.value, "value"):
                if kw.arg not in column.keys():
                    column["custom_column_props"][kw.arg] = kw.value.value
                else:
                    # upsert_strategy is a special case
                    if hasattr(kw.value, "attr"):
                        column[kw.arg] = kw.value.attr
                    else:
                        column[kw.arg] = kw.value.value
            else:
                if not hasattr(kw.value, "keywords"):
                    continue
                # An Array column that has a base_column
                column_params = ", ".join(
                    [f"{kw2.arg}={kw2.value.value}" for kw2 in kw.value.keywords]
                )
                column["custom_column_props"][
                    kw.arg
                ] = f"{kw.value.func.id}({column_params})"
        if column["db_name"] is None:
            column["db_name"] = column["name"]
        if column["name"] is None:
            return None
        if column["custom_column_props"] == {}:
            del column["custom_column_props"]
        if column["nullable"] is None:
            column["nullable"] = (
                not column["required"] if column["required"] is not None else True
            )
        return column
    return None
