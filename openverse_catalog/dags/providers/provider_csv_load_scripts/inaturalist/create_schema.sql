CREATE SCHEMA IF NOT EXISTS inaturalist;
COMMIT;
SELECT schema_name
FROM information_schema.schemata WHERE schema_name = 'inaturalist';
