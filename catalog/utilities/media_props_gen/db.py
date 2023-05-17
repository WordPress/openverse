import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal


LOCAL_POSTGRES_FOLDER = Path(__file__).parents[3] / "docker" / "upstream_db"
SQL_PATH = {
    "image": LOCAL_POSTGRES_FOLDER / "0003_openledger_image_schema.sql",
    "audio": LOCAL_POSTGRES_FOLDER / "0006_openledger_audio_schema.sql",
}
sql_types = [
    "integer",
    "boolean",
    "uuid",
    "double precision",
    "jsonb",
    "timestamp with time zone",
    "character varying",
]
sql_type_regex = re.compile(f"({'|'.join(sql_types)})")
MediaType = Literal["audio", "image"]


@dataclass
class FieldSqlInfo:
    nullable: bool
    datatype: str
    constraint: str


def create_db_props_dict(
    media_type: MediaType,
) -> dict[Any, Any] | dict[Any, dict[str, FieldSqlInfo]]:
    """
    Parse the DDL for a media type and returns a list of field
    sql definitions.
    """

    create_table_regex = re.compile(r"CREATE\s+TABLE\s+\w+\.(\w+)\s+\(([\s\S]*?)\);")
    sql_path = SQL_PATH[media_type]

    with open(sql_path) as f:
        contents = f.read()
        table_description_matches = create_table_regex.search(contents)
    if not table_description_matches:
        print(f"Could not find table description for {media_type} in {sql_path}")
        return {}
    table_name = table_description_matches.group(1)
    if table_name != media_type:
        print(f"Table name {table_name} does not match media type {media_type}")
        return {}
    field_descriptions = [
        field.strip()
        for field in table_description_matches.group(2).split("\n")
        if field.strip()
    ]
    fields = {}
    for field in field_descriptions:
        field_name = field.split(" ")[0]
        # False if "not null" in field.lower() else True
        field_constraint = ""
        try:
            field_type = sql_type_regex.search(field).group(1)
            if field_type == "character varying":
                char_limit = field.split("(")[1].split(")")[0]
                field_constraint = f"({char_limit})"

            if "[]" in field:
                field_type = f"array of {field_type}"
        except AttributeError:
            raise ValueError(f"Could not find type for field {field_name} in {field}")

        fields[field_name] = {
            "sql": FieldSqlInfo(
                nullable="NOT NULL" not in field,
                datatype=field_type,
                constraint=field_constraint,
            )
        }
    return fields
