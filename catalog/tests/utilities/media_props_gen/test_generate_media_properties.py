from unittest.mock import patch

import pytest

from catalog.utilities.media_props_gen.db import FieldSqlInfo
from catalog.utilities.media_props_gen.generate_media_properties import (
    generate_db_props_string,
    generate_markdown_doc,
)


DIRECTORY = "catalog.utilities.media_props_gen"
MODULE = f"{DIRECTORY}.generate_media_properties"

# Sample mock data
markdown_descriptions_mock = "Markdown Descriptions"
tables_mock = {"image": "Image Table Markdown", "audio": "Audio Table Markdown"}
long_form_doc_mock = "Long Form Documentation Mock"


@pytest.fixture
def props_source_mock():
    with patch(
        f"{MODULE}.parse_props_from_source",
        return_value=(markdown_descriptions_mock, tables_mock, long_form_doc_mock),
    ) as mock:
        yield mock


def test_generate_markdown_doc(props_source_mock):
    preamble_mock = "Preamble Content"
    postamble_mock = "Postamble Content"

    with patch(f"{MODULE}.PREAMBLE", preamble_mock), patch(
        f"{MODULE}.POSTAMBLE", postamble_mock
    ):
        result = generate_markdown_doc()

    expected_result = f"""{preamble_mock}
## Image Properties\n{tables_mock["image"]}
## Audio Properties\n{tables_mock["audio"]}
## Media Property Descriptions\n{long_form_doc_mock}\n
---\n\n{postamble_mock}"""

    assert result == expected_result


@pytest.mark.parametrize(
    "field,expected_output",
    [
        pytest.param(
            FieldSqlInfo(
                name="identifier", nullable=False, datatype="uuid", constraint=""
            ),
            ("identifier", "uuid, non-nullable"),
            id="uuid_non_nullable",
        ),
        pytest.param(
            FieldSqlInfo(
                name="created_on",
                nullable=False,
                datatype="timestamp with time zone",
                constraint="",
            ),
            ("created_on", "timestamp with time zone, non-nullable"),
            id="timestamp_non_nullable",
        ),
        pytest.param(
            FieldSqlInfo(
                name="ingestion_type",
                nullable=True,
                datatype="character varying",
                constraint="(80)",
            ),
            ("ingestion_type", "character varying (80), nullable"),
            id="varchar_nullable_with_constraint",
        ),
        pytest.param(
            FieldSqlInfo(
                name="url",
                nullable=False,
                datatype="character varying",
                constraint="(3000)",
            ),
            ("url", "character varying (3000), non-nullable"),
            id="varchar_non_nullable_with_constraint",
        ),
        pytest.param(
            FieldSqlInfo(
                name="meta_data", nullable=True, datatype="jsonb", constraint=""
            ),
            ("meta_data", "jsonb, nullable"),
            id="jsonb_nullable",
        ),
        pytest.param(
            FieldSqlInfo(
                name="watermarked", nullable=True, datatype="boolean", constraint=""
            ),
            ("watermarked", "boolean, nullable"),
            id="boolean_nullable",
        ),
        pytest.param(
            FieldSqlInfo(
                name="standardized_popularity",
                nullable=True,
                datatype="double precision",
                constraint="",
            ),
            ("standardized_popularity", "double precision, nullable"),
            id="double_precision_nullable",
        ),
    ],
)
def test_generate_db_props_string(field, expected_output):
    field_name, props_string = generate_db_props_string(field)
    assert field_name == f"[`{expected_output[0]}`](#{expected_output[0]})"
    assert props_string == expected_output[1]
