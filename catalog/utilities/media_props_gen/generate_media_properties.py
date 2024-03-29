"""Automatic media properties generation."""

import logging
import sys
from dataclasses import dataclass
from pathlib import Path


# Avoid import error in tests
sys.path.insert(0, str(Path(__file__).parents[3]))

from catalog.utilities.media_props_gen.helpers.column_parser import (
    parse_python_columns,
)

# noqa: E402
from catalog.utilities.media_props_gen.helpers.db import (
    FieldSqlInfo,
    create_db_props_dict,
)

# noqa: E402
from catalog.utilities.media_props_gen.helpers.md import Md  # noqa: E402
from common.constants import MEDIA_TYPES  # noqa: E402


log = logging.getLogger(__name__)
# Silence noisy modules
logging.getLogger("common.storage.media").setLevel(logging.WARNING)

# Constants
DOCS = Path(__file__).parent / "docs"
DOC_MD_PATH = Path(__file__).parent / "media_properties.md"
SOURCE_MD_PATH = DOCS / "media_props.md"

PREAMBLE = open(DOCS / "preamble.md").read()
POSTAMBLE = open(DOCS / "postamble.md").read()


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


def generate_db_props_string(field: FieldSqlInfo) -> tuple[str, str]:
    constraint = f"{' ' + field.constraint if field.constraint else ''}"
    nullable = f"{'nullable' if field.nullable else 'non-nullable'}"
    props_string = f"{field.datatype}{constraint}, {nullable}"

    return f"[`{field.name}`](#{field.name})", props_string


def generate_media_props_table(media_properties) -> str:
    """Generate the markdown table with media properties."""

    # Convert the list of FieldInfo objects to a md table
    table = "| Name | DB Field | Python Column |\n"
    table += "| --- | --- | --- |\n"
    for field_name, field in media_properties.items():
        name, db_properties = generate_db_props_string(field["sql"])

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
            [f"{Md.heading(4, k)}{Md.line(v)}" for k, v in description.items() if v]
        )
        media_docs += prop_heading + prop_doc

    return media_docs


def parse_props_from_source() -> tuple[dict, dict, str]:
    """Parse the media property descriptions from the source code and `media_props.md`"""
    media_properties = generate_media_properties()
    markdown_descriptions = Md.parse(SOURCE_MD_PATH.read_text())
    tables = {}

    for media_type in MEDIA_TYPES:
        tables[media_type] = generate_media_props_table(media_properties[media_type])

    long_form_doc = generate_long_form_doc(markdown_descriptions, media_properties)
    return markdown_descriptions, tables, long_form_doc


def generate_markdown_doc() -> str:
    """
    Parse the media property descriptions from the source code and `media_props.md`
    Generate the tables with media properties database column and
    Python objects characteristics, and a long-form documentation for each property.
    """

    markdown_descriptions, tables, long_form_doc = parse_props_from_source()

    media_props_doc = f"""
{PREAMBLE}
{Md.heading(2, "Image Properties")}{tables["image"]}
{Md.heading(2, "Audio Properties")}{tables["audio"]}
{Md.heading(2, "Media Property Descriptions")}{long_form_doc}
{Md.horizontal_line + POSTAMBLE if POSTAMBLE else ''}
""".strip()
    return media_props_doc


def write_media_props_doc(path: Path = DOC_MD_PATH) -> None:
    """Generate the DAG documentation and write it to a file."""
    doc_text = generate_markdown_doc()
    log.info(f"Writing DAG doc to {path}")
    path.write_text(doc_text)


if __name__ == "__main__":
    write_media_props_doc()
