import os

from common.constants import AWS_CONN_ID


DAG_ID = "staging_database_restore"
PROD_IDENTIFIER = "prod-openverse-db"
STAGING_IDENTIFIER = "dev-openverse-db"
SKIP_VARIABLE = "SKIP_STAGING_DATABASE_RESTORE"
AWS_RDS_CONN_ID = os.environ.get("AWS_RDS_CONN_ID", AWS_CONN_ID)
