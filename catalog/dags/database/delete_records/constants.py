from datetime import datetime, timedelta


DAG_ID = "delete_records"
SLACK_USERNAME = "Upstream Delete Records"
SLACK_ICON = ":database:"
START_DATE = datetime(2023, 10, 25)
DAGRUN_TIMEOUT = timedelta(days=31 * 3)
CREATE_TIMEOUT = timedelta(hours=6)
DELETE_TIMEOUT = timedelta(hours=1)

CREATE_RECORDS_QUERY = """
    INSERT INTO {destination_table} ({destination_cols})
    SELECT {source_cols}
    FROM {source_table}
    {select_query}
    """
DELETE_RECORDS_QUERY = """
    DELETE FROM {table}
    {select_query}
    """
RETURN_ROW_COUNT = lambda c: c.rowcount  # noqa: E731
