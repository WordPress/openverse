import pytest

from catalog.utilities.media_props_gen.helpers.db import (
    FieldSqlInfo,
    get_table_description_matches,
    parse_field,
)


@pytest.mark.parametrize(
    "field_input,expected_output",
    [
        pytest.param(
            "id integer NOT NULL",
            FieldSqlInfo(name="id", nullable=False, datatype="integer", constraint=""),
            id="integer not null",
        ),
        pytest.param(
            "active boolean",
            FieldSqlInfo(
                name="active", nullable=True, datatype="boolean", constraint=""
            ),
            id="boolean nullable",
        ),
        pytest.param(
            "user_id uuid[]",
            FieldSqlInfo(
                name="user_id", nullable=True, datatype="array of uuid", constraint=""
            ),
            id="array of uuid",
        ),
        pytest.param(
            "payload jsonb NOT NULL",
            FieldSqlInfo(
                name="payload", nullable=False, datatype="jsonb", constraint=""
            ),
            id="jsonb not null",
        ),
        pytest.param(
            "created_at timestamp with time zone",
            FieldSqlInfo(
                name="created_at",
                nullable=True,
                datatype="timestamp with time zone",
                constraint="",
            ),
            id="timestamp with time zone",
        ),
        pytest.param(
            "name character varying(255) NOT NULL",
            FieldSqlInfo(
                name="name",
                nullable=False,
                datatype="character varying",
                constraint="(255)",
            ),
            id="character varying with constraint",
        ),
        pytest.param("invalid_field not_a_type", None, id="invalid type"),
    ],
)
def test_parse_field(field_input, expected_output):
    assert parse_field(field_input) == expected_output


# Example SQL statements for testing
sql_for_image = "CREATE TABLE public.image (id SERIAL PRIMARY KEY, name VARCHAR(255));"
sql_for_audio = "CREATE TABLE public.audio (id SERIAL PRIMARY KEY, title VARCHAR(255));"
non_matching_sql = (
    "CREATE TABLE public.video (id SERIAL PRIMARY KEY, description TEXT);"
)
no_table_sql = "This is not a SQL create table statement."


@pytest.mark.parametrize(
    "media_type,sql_text,expected_table_name",
    [
        ("image", sql_for_image, "image"),
        ("audio", sql_for_audio, "audio"),
        ("image", non_matching_sql, None),
        ("audio", no_table_sql, None),
    ],
)
def test_get_table_description_matches(media_type, sql_text, expected_table_name):
    result = get_table_description_matches(sql_text, media_type)
    if expected_table_name:
        assert result is not None
        assert result.group(1) == expected_table_name
    else:
        assert result is None
