CREATE_SQL = """
DROP TABLE IF EXISTS {temp_table_name};
CREATE UNLOGGED TABLE {temp_table_name} (
    row_id SERIAL,
    identifier uuid NOT NULL,
    {column} TEXT
);
"""

# See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PostgreSQL.S3Import.html#aws_s3.table_import_from_s3
IMPORT_SQL = """
SELECT aws_s3.table_import_from_s3(
    '{temp_table_name}', 'identifier, {column}', 'DELIMITER E''\t'' CSV',
    '{bucket}', '{s3_path_to_file}', '{aws_region}'
);
"""
