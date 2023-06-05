from datetime import datetime, timedelta


DAG_ID = "batched_update"
START_DATE = datetime(2023, 5, 1)
SLACK_USERNAME = "Upstream Batched Update"
SLACK_ICON = ":database:"

DEFAULT_BATCH_SIZE = 100  # 10_000
DAGRUN_TIMEOUT = timedelta(days=31 * 3)
SELECT_TIMEOUT = timedelta(hours=24)
UPDATE_TIMEOUT = timedelta(days=30 * 3)  # 3 months

# Timeout for an individual batch, given in seconds
DEFAULT_UPDATE_BATCH_TIMEOUT = 60 * 60  # 1 hour

TEMP_TABLE_NAME = "{query_id}_rows_to_update"
CREATE_TEMP_TABLE_QUERY = """
    CREATE TABLE {temp_table_name} AS
    SELECT ROW_NUMBER() OVER() row_id, identifier
    FROM {table_name}
    {select_query}
    AND updated_on < NOW();
    """
CREATE_TEMP_TABLE_INDEX_QUERY = "CREATE INDEX ON {temp_table_name}(row_id)"
UPDATE_BATCH_QUERY = """
    UPDATE {table_name}
    {update_query}
    WHERE identifier in (
        SELECT identifier FROM {temp_table_name}
        WHERE row_id >= {batch_start} AND row_id < {batch_end}
        FOR UPDATE SKIP LOCKED
    );
    """
DROP_TABLE_QUERY = "DROP TABLE IF EXISTS {temp_table_name} CASCADE;"
RETURN_ROW_COUNT = lambda c: c.rowcount  # noqa: E731
