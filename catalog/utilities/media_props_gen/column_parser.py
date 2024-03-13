import ast
import dataclasses
from dataclasses import dataclass
from pathlib import Path


COLUMNS_PATH = Path(__file__).parents[2] / "dags" / "common" / "storage" / "columns.py"

COLUMNS_URL = "https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py"  # noqa: E501

CODE = ast.parse(COLUMNS_PATH.read_text())


@dataclass
class ColumnDefinition:
    name: str
    start_lineno: int
    end_lineno: int

    def __str__(self):
        return f"[{self.name}]({COLUMNS_URL}#L{self.start_lineno}-L{self.end_lineno})"


# Dictionary of all types of columns with their line numbers for hyperlinks
COLUMN_DEFINITIONS = {
    item.name: ColumnDefinition(
        name=item.name, start_lineno=item.lineno, end_lineno=item.end_lineno
    )
    for item in ast.iter_child_nodes(CODE)
    if isinstance(item, ast.ClassDef) and item.name.endswith("Column")
}


@dataclass
class Column:
    name: str | None = None
    db_name: str | None = None
    python_type: str | None = None
    upsert_strategy: str | None = None
    nullable: bool | None = None
    required: bool = False

    def __post_init__(self):
        """
        Set `nullable` value based on the value of `required`. If required is true,
        then the media item is discarded if the column is null.
        This mean that the column cannot have `None` as a value.
        """
        if self.nullable is None:
            self.nullable = True if self.required is None else not self.required
        if self.upsert_strategy is None:
            if self.python_type == "JSONColumn":
                self.upsert_strategy = "merge_jsonb_objects"
            elif self.python_type == "ArrayColumn":
                self.upsert_strategy = "merge_array"
            else:
                self.upsert_strategy = "newest_non_null"

    def __str__(self):
        name = (
            f'name="{self.name}", '
            if self.db_name and self.db_name != self.name
            else ""
        )
        res = name + ", ".join(
            [
                f"{f}={v}"
                for f in COLUMN_PROPS
                if (v := getattr(self, f)) is not None
                and f not in ["name", "db_name", "python_type"]
            ]
        )
        return f"{COLUMN_DEFINITIONS[self.python_type]} (`{res}`)"


COLUMN_PROPS = [field.name for field in dataclasses.fields(Column)]


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
    # Extracts all the assignments of the form `column_name = <Type>Column(...)`
    cols: list[tuple[str, ast.Call]] = [
        (item.value.func.id, item.value)
        for item in ast.iter_child_nodes(CODE)
        if isinstance(item, ast.Assign)
        and isinstance(item.value, ast.Call)
        and isinstance(item.value.func, ast.Name)
        and item.value.func.id.endswith("Column")
        and item.value.func.id != "Column"
    ]

    columns = {}
    for col_python_type, col in cols:
        parsed_column = Column(
            python_type=col_python_type,
            **{
                col.arg: parse_col_argument_value(col.value)
                for col in col.keywords
                if col.arg in COLUMN_PROPS
            },
        )

        db_name = parsed_column.db_name or parsed_column.name
        columns[db_name] = f"{parsed_column}"

    return columns
