import logging
from textwrap import dedent

from airflow.models.abstractoperator import AbstractOperator
from psycopg2.errors import InvalidTextRepresentation

from common.constants import IMAGE, MediaType, SQLInfo
from common.loader import provider_details as prov
from common.loader.paths import _extract_media_type
from common.sql import RETURN_ROW_COUNT, PostgresHook
from common.storage import columns as col
from common.storage.columns import NULL, Column, UpsertStrategy
from common.storage.db_columns import setup_db_columns_for_media_type
from common.storage.tsv_columns import (
    COLUMNS,
    REQUIRED_COLUMNS,
    setup_tsv_columns_for_media_type,
)
from common.utils import setup_sql_info_for_media_type


logger = logging.getLogger(__name__)

LOAD_TABLE_NAME_STUB = "load_"
DB_USER_NAME = "deploy"
NOW = "NOW()"
FALSE = "'f'"
OLDEST_PER_PROVIDER = {
    prov.FLICKR_DEFAULT_PROVIDER: "6 months 18 days",
    prov.EUROPEANA_DEFAULT_PROVIDER: "3 months 9 days",
    prov.WIKIMEDIA_DEFAULT_PROVIDER: "6 months 18 days",
    prov.SMITHSONIAN_DEFAULT_PROVIDER: "8 days",
    prov.BROOKLYN_DEFAULT_PROVIDER: "1 month 3 days",
    prov.CLEVELAND_DEFAULT_PROVIDER: "1 month 3 days",
    prov.VICTORIA_DEFAULT_PROVIDER: "1 month 3 days",
    prov.NYPL_DEFAULT_PROVIDER: "1 month 3 days",
    prov.RAWPIXEL_DEFAULT_PROVIDER: "1 month 3 days",
    prov.SCIENCE_DEFAULT_PROVIDER: "1 month 3 days",
    prov.SMK_DEFAULT_PROVIDER: "1 month 3 days",
}

CURRENT_TSV_VERSION = "001"


def create_column_definitions(table_columns: list[Column], is_loading=True):
    """
    Create column definitions for a table.

    Loading table should not have 'NOT NULL' constraints: all TSV values
    are copied, and then the items without required columns are dropped.
    """
    definitions = [column.create_definition(is_loading) for column in table_columns]
    return ",\n  ".join(definitions)


@setup_tsv_columns_for_media_type
def create_loading_table(
    postgres_conn_id: str,
    identifier: str,
    *,
    media_type: str,
    tsv_columns: list[Column],
):
    """Create intermediary table and indices if they do not exist."""
    load_table = _get_load_table_name(identifier, media_type=media_type)
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=10.0,
    )
    columns_definition = f"{create_column_definitions(tsv_columns)}"
    table_creation_query = dedent(
        f"""
    CREATE UNLOGGED TABLE public.{load_table}(
    {columns_definition});
    """
    )

    def create_index(column, btree_column=None):
        btree_string = (
            f"{column}"
            if not btree_column
            else f"{btree_column}, md5(({column})::text)"
        )
        postgres.run(
            dedent(
                f"""
               CREATE INDEX IF NOT EXISTS {load_table}_{column}_key
               ON public.{load_table} USING btree ({btree_string});
               """
            )
        )

    postgres.run(table_creation_query)
    postgres.run(f"ALTER TABLE public.{load_table} OWNER TO {DB_USER_NAME};")
    create_index(col.PROVIDER.db_name, None)
    create_index(col.FOREIGN_ID.db_name, "provider")
    create_index(col.DIRECT_URL.db_name, "provider")
    return load_table


def load_local_data_to_intermediate_table(
    postgres_conn_id,
    tsv_file_name,
    identifier,
    max_rows_to_skip=10,
    task: AbstractOperator = None,
):
    media_type = _extract_media_type(tsv_file_name)
    load_table = _get_load_table_name(identifier, media_type=media_type)
    logger.info(f"Loading {tsv_file_name} into {load_table}")

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    load_successful = False

    while not load_successful and max_rows_to_skip >= 0:
        try:
            postgres.bulk_load(f"{load_table}", tsv_file_name)
            load_successful = True

        except InvalidTextRepresentation as e:
            line_number = _get_malformed_row_in_file(str(e))
            _delete_malformed_row_in_file(tsv_file_name, line_number)

        finally:
            max_rows_to_skip = max_rows_to_skip - 1

    if not load_successful:
        raise InvalidTextRepresentation(
            "Exceeded the maximum number of allowed defective rows"
        )


def _handle_s3_load_result(cursor) -> int:
    """
    Handle the results of the aws_s3.table_import_from_s3 function.

    Locally this will return an integer, but on AWS infrastructure it will return a
    string similar to:

    500 rows imported into relation "..." from file ... of ... bytes
    """
    result = cursor.fetchone()[0]
    if isinstance(result, str):
        result = int(result.split(" ", maxsplit=1)[0])
    return result


def load_s3_data_to_intermediate_table(
    postgres_conn_id,
    bucket,
    s3_key,
    identifier,
    media_type=IMAGE,
    task: AbstractOperator = None,
) -> int:
    load_table = _get_load_table_name(identifier, media_type=media_type)
    logger.info(f"Loading {s3_key} from S3 Bucket {bucket} into {load_table}")

    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )
    loaded = postgres.run(
        dedent(
            f"""
            SELECT aws_s3.table_import_from_s3(
              '{load_table}',
              '',
              'DELIMITER E''\t''',
              '{bucket}',
              '{s3_key}',
              'us-east-1'
            );
            """
        ),
        handler=_handle_s3_load_result,
    )
    logger.info(f"Successfully loaded {loaded} records from S3")
    return loaded


def clean_intermediate_table_data(
    postgres_conn_id: str,
    identifier: str,
    media_type: MediaType = IMAGE,
    task: AbstractOperator = None,
) -> tuple[int, int]:
    """
    Clean the data in the intermediate table.

    Necessary for old TSV files that have not been cleaned up, using `MediaStore` class:
    Removes any rows without any of the required fields:
    `url`, `license`, `license_version`, `foreign_id`.
    Also removes any duplicate rows that have the same `provider`
    and `foreign_id`.
    """
    load_table = _get_load_table_name(identifier, media_type=media_type)
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    missing_columns = 0
    for column in REQUIRED_COLUMNS:
        missing_columns += postgres.run(
            f"DELETE FROM {load_table} WHERE {column.db_name} IS NULL;",
            handler=RETURN_ROW_COUNT,
        )
    foreign_id_dup = postgres.run(
        dedent(
            f"""
            DELETE FROM {load_table} p1
            USING {load_table} p2
            WHERE
              p1.ctid < p2.ctid
              AND p1.{col.PROVIDER.db_name} = p2.{col.PROVIDER.db_name}
              AND MD5(p1.{col.FOREIGN_ID.db_name}) = MD5(p2.{col.FOREIGN_ID.db_name});
            """
        ),
        handler=RETURN_ROW_COUNT,
    )
    logger.info(
        f"{missing_columns} records missing columns, "
        f"{foreign_id_dup} records with duplicate foreign_ids"
    )
    return missing_columns, foreign_id_dup


def _is_tsv_column_from_different_version(
    column: Column, media_type: str, tsv_version: str
) -> bool:
    """
    Check that a column appears in the available columns for a TSV version.

    Check that column is a column that exists in TSV files (unlike the db-only
    columns like IDENTIFIER or CREATED_ON, or calculated values like
    STANDARDIZED_POPULARITY), but is not available for `tsv_version`.
    For example, Category column was added to Image TSV in version 001:
    >>> from common.storage import CATEGORY, DIRECT_URL
    >>> _is_tsv_column_from_different_version(CATEGORY, IMAGE, '000')
    True
    >>> _is_tsv_column_from_different_version(DIRECT_URL, IMAGE, '000')
    False
    >>> from common.storage import IDENTIFIER
    >>> _is_tsv_column_from_different_version(IDENTIFIER, IMAGE, '000')
    False
    >>> _is_tsv_column_from_different_version(STANDARDIZED_POPULARITY, IMAGE, '000')
    False
    """
    return (
        column not in COLUMNS[media_type][tsv_version]
        and column.upsert_strategy == UpsertStrategy.newest_non_null
    )


@setup_sql_info_for_media_type
@setup_db_columns_for_media_type
def upsert_records_to_db_table(
    postgres_conn_id: str,
    identifier: str,
    *,
    media_type: str,
    db_columns: list[Column],
    sql_info: SQLInfo,
    tsv_version: str = CURRENT_TSV_VERSION,
    task: AbstractOperator = None,
):
    """
    Upsert newly ingested records from loading table into the main db table.

    For tsv columns that do not exist in the `tsv_version` for `media_type`,
    NULL value is used.

    :param postgres_conn_id
    :param identifier
    :param media_type
    :param tsv_version:      The version of TSV being processed. This
    determines which columns are used in the upsert query.
    :param task              To be automagically passed by airflow.
    :return:
    """
    load_table = _get_load_table_name(identifier, media_type=media_type)
    logger.info(f"Upserting new records into {sql_info.media_table}.")
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    # Remove identifier column
    db_columns = db_columns[1:]
    column_inserts = {}
    column_conflict_values = {}
    for column in db_columns:
        args = []
        if column.db_name == col.STANDARDIZED_POPULARITY.db_name:
            args = [
                sql_info.standardized_popularity_fn,
            ]

        if column.upsert_strategy == UpsertStrategy.no_change:
            column_inserts[column.db_name] = column.get_insert_value()
        elif _is_tsv_column_from_different_version(column, media_type, tsv_version):
            column_inserts[column.db_name] = NULL
            column_conflict_values[column.db_name] = NULL
        else:
            column_conflict_values[column.db_name] = column.get_update_value(*args)
            # The direct_url is handled specially to ensure uniqueness and
            # should not be added to the column_inserts.
            if not column.db_name == col.DIRECT_URL.name:
                column_inserts[column.db_name] = column.get_insert_value(*args)

    upsert_conflict_string = ",\n    ".join(column_conflict_values.values())
    upsert_query = dedent(
        f"""
        INSERT INTO {sql_info.media_table} AS old
        ({col.DIRECT_URL.name}, {', '.join(column_inserts.keys())})
        SELECT DISTINCT ON ({col.DIRECT_URL.name}) {col.DIRECT_URL.name},
        {', '.join(column_inserts.values())}
        FROM {load_table} as new
        WHERE NOT EXISTS (
            SELECT {col.DIRECT_URL.name} from {sql_info.media_table}
            WHERE {col.DIRECT_URL.name} = new.{col.DIRECT_URL.name} AND
                MD5({col.FOREIGN_ID.name}) <> MD5(new.{col.FOREIGN_ID.name})
        )
        ON CONFLICT ({col.PROVIDER.db_name}, md5({col.FOREIGN_ID.db_name}))
        DO UPDATE SET
        {upsert_conflict_string}
        """
    )
    return postgres.run(upsert_query, handler=RETURN_ROW_COUNT)


def drop_load_table(
    postgres_conn_id,
    identifier,
    media_type: str = IMAGE,
):
    load_table = _get_load_table_name(identifier, media_type=media_type)
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id, default_statement_timeout=60
    )
    postgres.run(f"DROP TABLE IF EXISTS {load_table};")


def _get_load_table_name(
    identifier: str,
    media_type: str = IMAGE,
    load_table_name_stub: str = LOAD_TABLE_NAME_STUB,
) -> str:
    return f"{load_table_name_stub}{media_type}_{identifier}"


def _get_malformed_row_in_file(error_msg):
    error_list = error_msg.splitlines()
    copy_error = next((line for line in error_list if line.startswith("COPY")), None)
    assert copy_error is not None

    line_number = int(copy_error.split("line ")[1].split(",")[0])

    return line_number


def _delete_malformed_row_in_file(tsv_file_name, line_number):
    with open(tsv_file_name) as read_obj:
        lines = read_obj.readlines()

    with open(tsv_file_name, "w") as write_obj:
        for index, line in enumerate(lines):
            if index + 1 != line_number:
                write_obj.write(line)
