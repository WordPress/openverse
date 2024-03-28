import os
import uuid
from collections import namedtuple
from unittest import mock

from airflow.models import TaskInstance

from common.loader.sql import create_column_definitions
from common.storage import columns as col
from common.storage.db_columns import DELETED_IMAGE_TABLE_COLUMNS, IMAGE_TABLE_COLUMNS
from common.storage.tsv_columns import CURRENT_IMAGE_TSV_COLUMNS


POSTGRES_CONN_ID = os.getenv("TEST_CONN_ID")
POSTGRES_TEST_URI = os.getenv("AIRFLOW_CONN_POSTGRES_OPENLEDGER_TESTING")
S3_LOCAL_ENDPOINT = os.getenv("S3_LOCAL_ENDPOINT")
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")


LOADING_TABLE_COLUMN_DEFINITIONS = create_column_definitions(
    CURRENT_IMAGE_TSV_COLUMNS, is_loading=True
)

CREATE_LOAD_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
  {LOADING_TABLE_COLUMN_DEFINITIONS}
);"""

IMAGE_TABLE_COLUMN_DEFINITIONS = create_column_definitions(IMAGE_TABLE_COLUMNS)

CREATE_IMAGE_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
  {IMAGE_TABLE_COLUMN_DEFINITIONS}
);"""

UNIQUE_CONDITION_QUERY = (
    "CREATE UNIQUE INDEX {table}_provider_fid_idx"
    " ON public.{table}"
    " USING btree (provider, md5(foreign_identifier));"
    "CREATE UNIQUE INDEX {table}_identifier_key"
    " ON public.{table}"
    " USING btree (identifier);"
    "CREATE UNIQUE INDEX {table}_url_key"
    " ON public.{table}"
    " USING btree (url);"
)

DELETED_IMAGE_TABLE_COLUMN_DEFINITIONS = create_column_definitions(
    DELETED_IMAGE_TABLE_COLUMNS
)

CREATE_DELETED_IMAGE_TABLE_QUERY = f"""CREATE TABLE public.{{}} (
    {DELETED_IMAGE_TABLE_COLUMN_DEFINITIONS}
);"""

DELETED_IMAGE_TABLE_UNIQUE_CONDITION_QUERY = (
    "CREATE UNIQUE INDEX {table}_provider_fid_idx"
    " ON public.{table}"
    " USING btree (provider, md5(foreign_identifier));"
)

PostgresRef = namedtuple("PostgresRef", ["cursor", "connection"])
ti = mock.Mock(spec=TaskInstance)
ti.xcom_pull.return_value = None

COLUMN_NAMES = [column.db_name for column in IMAGE_TABLE_COLUMNS]

# ids for main database columns
updated_idx = COLUMN_NAMES.index(col.UPDATED_ON.db_name)
ingestion_idx = COLUMN_NAMES.index(col.INGESTION_TYPE.db_name)
provider_idx = COLUMN_NAMES.index(col.PROVIDER.db_name)
source_idx = COLUMN_NAMES.index(col.SOURCE.db_name)
fid_idx = COLUMN_NAMES.index(col.FOREIGN_ID.db_name)
land_url_idx = COLUMN_NAMES.index(col.LANDING_URL.db_name)
url_idx = COLUMN_NAMES.index(col.DIRECT_URL.db_name)
thm_idx = COLUMN_NAMES.index(col.THUMBNAIL.db_name)
filesize_idx = COLUMN_NAMES.index(col.FILESIZE.db_name)
license_idx = COLUMN_NAMES.index(col.LICENSE.db_name)
version_idx = COLUMN_NAMES.index(col.LICENSE_VERSION.db_name)
creator_idx = COLUMN_NAMES.index(col.CREATOR.db_name)
creator_url_idx = COLUMN_NAMES.index(col.CREATOR_URL.db_name)
title_idx = COLUMN_NAMES.index(col.TITLE.db_name)
metadata_idx = COLUMN_NAMES.index(col.META_DATA.db_name)
tags_idx = COLUMN_NAMES.index(col.TAGS.db_name)
synced_idx = COLUMN_NAMES.index(col.LAST_SYNCED.db_name)
removed_idx = COLUMN_NAMES.index(col.REMOVED.db_name)
watermarked_idx = COLUMN_NAMES.index(col.WATERMARKED.db_name)
width_idx = COLUMN_NAMES.index(col.WIDTH.db_name)
height_idx = COLUMN_NAMES.index(col.HEIGHT.db_name)
standardized_popularity_idx = COLUMN_NAMES.index(col.STANDARDIZED_POPULARITY.db_name)

DELETED_MEDIA_COLUMN_NAMES = [column.db_name for column in DELETED_IMAGE_TABLE_COLUMNS]
deleted_reason_idx = DELETED_MEDIA_COLUMN_NAMES.index(col.DELETED_REASON.db_name)


def create_query_values(
    column_values: dict,
    columns=None,
):
    if columns is None:
        columns = CURRENT_IMAGE_TSV_COLUMNS
    result = []
    for column in columns:
        val = column_values.get(column.db_name)
        if val is None:
            val = "null"
        else:
            val = f"'{str(val)}'"
        result.append(val)
    return ",".join(result)


def make_insert_query(table: str, values: str) -> str:
    """Return an SQL insert statement for the given table with the given values"""
    return f"INSERT INTO {table} VALUES({values});"


def _get_insert_query(image_table, values: dict):
    # Append the required identifier
    values[col.IDENTIFIER.db_name] = uuid.uuid4()

    query_values = create_query_values(values, columns=IMAGE_TABLE_COLUMNS)

    return make_insert_query(image_table, query_values)


def load_sample_data_into_image_table(image_table, postgres, records):
    for record in records:
        load_data_query = _get_insert_query(image_table, record)
        postgres.cursor.execute(load_data_query)

    postgres.connection.commit()
