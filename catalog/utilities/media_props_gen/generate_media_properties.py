"""Automatic media properties generation."""

import logging
from dataclasses import dataclass
from pathlib import Path

from column_parser import parse_python_columns
from db import MediaType, create_db_props_dict
from md import Md


log = logging.getLogger(__name__)
# Silence noisy modules
logging.getLogger("common.storage.media").setLevel(logging.WARNING)

# Constants
PARENT = Path(__file__).parent
DOC_MD_PATH = PARENT / "media_properties.md"
SOURCE_MD_PATH = PARENT / "media_props.md"

PREAMBLE = open(Path(__file__).parent / "preamble.md").read()

MEDIA_TYPES: list[MediaType] = ["audio", "image"]


@dataclass
class FieldInfo:
    name: str
    nullable: bool
    datatype: str
    constraint: str
    python_column: str = ""


def generate_media_properties() -> dict:
    """
    Generate a dictionary documenting each property of the media items.
    For each property, return the database field and the Python object shape.
    """
    media_props = {}
    python_columns = parse_python_columns()

    for media_type in MEDIA_TYPES:
        media_props[media_type] = create_db_props_dict(media_type)

        # Add the python column properties to the media properties dictionary
        for prop in media_props[media_type].keys():
            media_props[media_type][prop]["python_column"] = python_columns.get(
                prop, ""
            )

    return media_props


def generate_db_props_string(field_name: str, field: dict) -> tuple[str, str]:
    field_sql = field["sql"]

    constraint = f"{' '+field_sql.constraint if field_sql.constraint else ''}"
    nullable = f"{'nullable' if field_sql.nullable else 'non-nullable'}"
    props_string = f"{field_sql.datatype}{constraint}, {nullable}"

    return f"[`{field_name}`](#{field_name})", props_string


def generate_media_props_table(media_properties) -> str:
    """Generate the markdown table with media properties."""

    # Convert the list of FieldInfo objects to a md table
    table = "| Name | DB Field | Python Column |\n"
    table += "| --- | --- | --- |\n"
    for field_name, field in media_properties.items():
        name, db_properties = generate_db_props_string(field_name, field)

        table += (
            f"| {name} | {db_properties} | " f"{field.get('python_column', '')} |\n"
        )
    return table


def generate_long_form_doc(markdown_descriptions: dict, media_properties: dict) -> str:
    """
    Generate the long-form markdown documentation for each media property.
    Uses the markdown descriptions from the `media_props.md` source file.
    Also uses `media_properties` dictionary to set which media types have
    the specific properties.
    """
    media_docs = ""
    for prop, description in markdown_descriptions.items():
        prop_heading = f"{Md.heading(3, prop)}"

        media_types = [
            f"`{media_type}`"
            for media_type, value in media_properties.items()
            if prop in value.keys()
        ]
        prop_heading += f"_Media Types_: {', '.join(media_types)}\n\n"

        prop_doc = "".join(
            [f"{Md.heading(4, k)}{Md.line(v)}" for k, v in description.items()]
        )
        media_docs += prop_heading + prop_doc + Md.horizontal_line

    return media_docs


def generate_markdown_doc() -> str:
    """
    Parse the media property descriptions from the source code and `media_props.md`
    Generate the tables with media properties database column and
    Python objects characteristics, and a long-form documentation for each property.
    """
    media_properties = generate_media_properties()
    markdown_descriptions = Md.parse(SOURCE_MD_PATH)

    image_table = generate_media_props_table(media_properties["image"])
    audio_table = generate_media_props_table(media_properties["audio"])

    long_form_doc = generate_long_form_doc(markdown_descriptions, media_properties)

    media_props_doc = f"""
{PREAMBLE}
{Md.heading(2, "Image Properties")}{image_table}
{Md.heading(2, "Audio Properties")}{audio_table}
{Md.heading(2, "Media Property Descriptions")}{long_form_doc}
""".strip()
    return media_props_doc


def write_media_props_doc(path: Path = DOC_MD_PATH) -> None:
    """Generate the DAG documentation and write it to a file."""
    doc_text = generate_markdown_doc()
    log.info(f"Writing DAG doc to {path}")
    path.write_text(doc_text)


if __name__ == "__main__":
    write_media_props_doc()
