_ID_FORMAT = "{}-openverse-db"

DAG_ID = "staging_database_restore"
# These identifiers must match the existing databases,
# and follow the legacy environment names, where
# "prod" is used for production and "dev" is used for staging
PROD_IDENTIFIER = _ID_FORMAT.format("prod")
STAGING_IDENTIFIER = _ID_FORMAT.format("dev")
TEMP_IDENTIFIER = _ID_FORMAT.format("dev-next")
OLD_IDENTIFIER = _ID_FORMAT.format("dev-old")

SAFE_TO_MUTATE = {STAGING_IDENTIFIER, TEMP_IDENTIFIER, OLD_IDENTIFIER}

SKIP_VARIABLE = "SKIP_STAGING_DATABASE_RESTORE"
SLACK_USERNAME = "Staging Database Restore"
SLACK_ICON = ":database-pink:"
