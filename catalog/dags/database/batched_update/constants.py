from datetime import datetime, timedelta


DAG_ID = "batched_update"
AUTOMATED_DAG_ID = f"automated_{DAG_ID}"
START_DATE = datetime(2023, 5, 1)
SLACK_USERNAME = "Upstream Batched Update"
SLACK_ICON = ":database:"

DEFAULT_BATCH_SIZE = 10_000
SELECT_TIMEOUT = timedelta(hours=24)
UPDATE_TIMEOUT = timedelta(days=30)  # 1 month
DAGRUN_TIMEOUT = UPDATE_TIMEOUT + SELECT_TIMEOUT

# Task IDs used for branching operator
GET_EXPECTED_COUNT_TASK_ID = "get_expected_update_count"
CREATE_TEMP_TABLE_TASK_ID = "select_rows_to_update"

# Timeout for an individual batch, given in seconds
DEFAULT_UPDATE_BATCH_TIMEOUT = 60 * 60  # 1 hour

TEMP_TABLE_NAME = "{query_id}_rows_to_update"
CREATE_TEMP_TABLE_QUERY = """
    CREATE TABLE {temp_table_name} AS
    SELECT ROW_NUMBER() OVER() row_id, identifier
    FROM {table_name}
    {select_query};
    """
CREATE_TEMP_TABLE_INDEX_QUERY = "CREATE INDEX ON {temp_table_name}(row_id)"
SELECT_TEMP_TABLE_COUNT_QUERY = """
    SELECT COUNT(*)
    FROM {temp_table_name};
    """
UPDATE_BATCH_QUERY = """
    UPDATE {table_name}
    {update_query}
    WHERE identifier in (
        SELECT identifier FROM {temp_table_name}
        WHERE row_id > {batch_start} AND row_id <= {batch_end}
        FOR UPDATE SKIP LOCKED
    );
    """
DROP_TABLE_QUERY = "DROP TABLE IF EXISTS {temp_table_name} CASCADE;"
