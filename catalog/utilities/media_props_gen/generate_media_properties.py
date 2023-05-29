"""Automatic media properties generation."""
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from column_parser import parse_python_columns


log = logging.getLogger(__name__)
# Silence noisy modules
logging.getLogger("common.storage.media").setLevel(logging.WARNING)

# Constants
DOC_MD_PATH = Path(__file__).parent / "media_properties.md"
SOURCE_MD_PATH = Path(__file__).parent / "media_props.md"
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


@dataclass
class FieldInfo:
    name: str
    nullable: bool
    datatype: str
    constraint: str
    python_column: str = ""


@dataclass
class FieldSqlInfo:
    nullable: bool
    datatype: str
    constraint: str


def create_db_props_dict(
    media_type: Literal["image", "audio"]
) -> dict[str, FieldSqlInfo]:
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
        False if "not null" in field.lower() else True
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


def add_column_props(media_props, python_columns):
    """Add the python column properties to the media properties dictionary."""
    for prop in media_props.keys():
        if not (python_prop := python_columns.get(prop)):
            print(f"Column {prop} not found in table")
            python_prop = ""
        media_props[prop]["python_column"] = python_prop
    return media_props


def parse_markdown() -> dict[str, str]:
    """
    Parse the markdown documentation file and return a dictionary with the
    field name as key and the description as value.
    """
    with open(SOURCE_MD_PATH) as f:
        contents = [line for line in f.readlines() if line.strip()]
    current_field = ""
    properties = {}
    property = ""
    value = {}
    for i, line in enumerate(contents):
        if line.startswith("# "):
            if current_field and value:
                properties[current_field] = value
            current_field = line.replace("# ", "").strip()
            value = {}
            continue
        elif line.startswith("## "):
            property = line.replace("## ", "").strip()
            value[property] = ""
            continue
        else:
            value[property] += line

    return properties


def generate_media_props() -> dict:
    """
    Generate a dictionary with the media properties from the database,
    python code and markdown documentation files.
    """
    media_props = {}
    python_columns = parse_python_columns()

    for media_type in ["image", "audio"]:
        media_props[media_type] = create_db_props_dict(media_type)
        media_props[media_type] = add_column_props(
            media_props[media_type], python_columns
        )
    return media_props


def generate_media_props_table(media_properties) -> str:
    """Generate the table with media properties."""

    # Convert the list of FieldInfo objects to a md table
    table = "| DB Field | DB Nullable | DB Type | Python Column | Description | \n"
    table += "| --- | --- | --- | --- | --- | \n"
    media_docs = {}
    for field_name, field in media_properties.items():
        field_sql = field["sql"]
        field_db_type = (
            field_sql.datatype
            if not field_sql.constraint
            else f"{field_sql.datatype} {field_sql.constraint}"
        )
        table += (
            f"| `{field_name}` | {field_sql.nullable} | "
            f"{field_db_type} | {field.get('python_column', '')} | "
            f"{media_docs.get(field_name) or ''}\n"
        )

    return table


def generate_media_props_doc(
    markdown_descriptions: dict, media_properties: dict
) -> str:
    """Generate the long-form documentation for each media property."""
    media_docs = ""
    for prop, description in markdown_descriptions.items():
        prop_heading = f"### {prop}\n\n"
        media_types = []
        for media_type, value in media_properties.items():
            print(prop in value.keys())
            if prop in value.keys():
                media_types.append(media_type)

        print(f"\nMedia Types: {', '.join(media_types)}\n")
        prop_heading += f"Media Types: {', '.join(media_types)}\n\n"
        prop_doc = ""
        for name, value in description.items():
            if value:
                prop_doc += f"#### {name}\n\n"
                prop_doc += f"{value}\n\n"
        if prop_doc:
            media_docs += prop_heading + prop_doc

    return media_docs


def generate_markdown_doc(
    media_properties: dict[str, dict], markdown_descriptions: dict[str, dict]
) -> str:
    """
    Generate the tables with media properties database column and
    Python objects characteristics.
    """
    with open(Path(__file__).parent / "preamble.md") as f:
        preamble = f.read()
    media_props_doc = f"""{preamble}
## Image Properties\n
{generate_media_props_table(media_properties["image"])}
"""  # noqa 501
    media_props_doc += f"""## Audio Properties\n
{generate_media_props_table(media_properties["audio"])}
"""
    media_props_doc += f"""## Media Property Descriptions\n
{generate_media_props_doc(markdown_descriptions, media_properties)}
    """
    return media_props_doc


def write_media_props_doc(path: Path = DOC_MD_PATH) -> None:
    """Generate the DAG documentation and write it to a file."""
    media_properties = generate_media_props()
    markdown_descriptions = parse_markdown()
    doc_text = generate_markdown_doc(media_properties, markdown_descriptions)
    log.info(f"Writing DAG doc to {path}")
    path.write_text(doc_text)


if __name__ == "__main__":
    write_media_props_doc()
