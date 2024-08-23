from datetime import timedelta


DAG_ID = "add_rekognition_labels"
SLACK_USERNAME = "Rekognition Label Insertion"
SLACK_ICON = ":robot:"
PROVIDER = "rekognition"

# File location in S3, can be overridden by a Variable at runtime
S3_BUCKET = "s3://migrated-cccatalog-archives"
S3_FILE_PREFIX = "kafka/image_analysis_labels-2020-12-17.txt"
# Current position in the file
CURRENT_POS_VAR_NAME = "rekognition_label_insertion_current_position"
# In-memory buffer for records to insert into the temporary table
MEMORY_BUFFER_SIZE = 1_000
# In-memory buffer for reading from the file in S3
# See: https://github.com/piskvorky/smart_open/blob/a55794dee992dcebc3de23143c2c4a43ed3cc183/smart_open/s3.py#L70
FILE_BUFFER_SIZE = 5 * 1024 * 1024  # 5MB
# Timeout for inserting a batch of records into the temporary table
INSERT_TIMEOUT = timedelta(minutes=2)

# Task IDs used for branching operator
INSERT_LABELS_TASK_ID = "parse_and_insert_labels"
CREATE_TEMP_TABLE_TASK_ID = "create_loading_table"

# Timeout for inserting a batch of records into the temporary table
DEFAULT_INSERT_BATCH_TIMEOUT = 60 * 60  # 1 hour

TEMP_TABLE_NAME = "rekognition_label_insertion"
# Copy the table definition using a query which will return no rows, but
# prevents us from having to be explicit about data types
CREATE_TEMP_TABLE_QUERY = f"""
    CREATE TABLE {TEMP_TABLE_NAME} AS
    SELECT identifier, tags
    FROM image
    WHERE 0=1;
    """
CREATE_TEMP_TABLE_INDEX_QUERY = f"CREATE INDEX ON {TEMP_TABLE_NAME}(identifier)"
SELECT_TEMP_TABLE_COUNT_QUERY = f"""
    SELECT COUNT(*)
    FROM {TEMP_TABLE_NAME};
    """
# VALUES here will be interpolated by `execute_values` from psycopg2.extras
INSERT_BATCH_QUERY = f"""
    INSERT INTO {TEMP_TABLE_NAME} (identifier, tags)
    VALUES %s;
"""
DROP_TABLE_QUERY = "DROP TABLE IF EXISTS {TEMP_TABLE_NAME} CASCADE;"
