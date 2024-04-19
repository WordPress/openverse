import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common.constants import MediaType


LOCAL_POSTGRES_FOLDER = Path(__file__).parents[4] / "docker" / "upstream_db"
SQL_PATH = {
    "image": LOCAL_POSTGRES_FOLDER / "0003_openledger_image_schema.sql",
    "audio": LOCAL_POSTGRES_FOLDER / "0006_openledger_audio_schema.sql",
}
SQL_TYPES = [
    "integer",
    "boolean",
    "uuid",
    "double precision",
    "jsonb",
    "timestamp with time zone",
    "character varying",
]
SQL_TYPE_REGEX = re.compile(f"({'|'.join(SQL_TYPES)})")
CREATE_TABLE_REGEX = re.compile(r"CREATE\s+TABLE\s+\w+\.(\w+)\s+\(([\s\S]*?)\);")


@dataclass
class FieldSqlInfo:
    name: str
    nullable: bool
    datatype: str
    constraint: str


def get_table_description_matches(
    sql_file_contents: str, media_type: MediaType
) -> re.Match[str] | None:
    """
    Return the table description matches for a given media type or None if
    the table description could not be found or the table name is not `media_type`.
    """
    table_description_matches = CREATE_TABLE_REGEX.search(sql_file_contents)

    if not table_description_matches:
        logging.warning(f"Could not find table description for {media_type}")
        return None
    table_name = table_description_matches.group(1)
    if table_name != media_type:
        logging.warning(
            f"Table name {table_name} does not match media type {media_type}"
        )
        return None
    return table_description_matches


def parse_field(field: str) -> FieldSqlInfo | None:
    field_name = field.split(" ")[0]
    field_constraint = ""
    try:
        field_type = SQL_TYPE_REGEX.search(field).group(1)
        if field_type == "character varying":
            char_limit = field.split("(")[1].split(")")[0]
            field_constraint = f"({char_limit})"

        if "[]" in field:
            field_type = f"array of {field_type}"
    except AttributeError:
        logging.warning(f"Could not find type for field {field_name} in {field}")
        return None

    return FieldSqlInfo(
        name=field_name,
        nullable="NOT NULL" not in field,
        datatype=field_type,
        constraint=field_constraint,
    )


def create_db_props_dict(
    media_type: MediaType,
) -> dict[Any, Any] | dict[Any, dict[str, FieldSqlInfo]]:
    """
    Parse the DDL for a media type and returns a list of field
    sql definitions.
    """
    sql_path = SQL_PATH[media_type]
    logging.debug(f"Reading SQL file {sql_path}")

    if not (matches := get_table_description_matches(sql_path.read_text(), media_type)):
        return {}

    field_descriptions = [
        field.strip() for field in matches.group(2).split("\n") if field.strip()
    ]
    fields = {}
    for field in field_descriptions:
        if field_sql_info := parse_field(field):
            fields[field_sql_info.name] = {"sql": field_sql_info}
    return fields
