from textwrap import dedent
from airflow.hooks.postgres_hook import PostgresHook


def upload_normalized_popularity(postgres_conn_id, in_tsv):
    """ Write the `normalized_score` field from `in_tsv` to the catalog. """
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    postgres.copy_expert(
        "CREATE TEMP TABLE temp_popularity "
        "  (identifier uuid, normalized_popularity text); "
        "COPY temp_popularity FROM STDIN WITH CSV HEADER DELIMITER E'\t'; "
        "UPDATE image SET meta_data = jsonb_set("
        "  meta_data, "
        "  '{normalized_popularity}',"
        "  temp_popularity.normalized_popularity::jsonb"
        ") FROM temp_popularity"
        "  WHERE image.identifier = temp_popularity.identifier;",
        in_tsv
    )


def select_percentiles(postgres_conn_id, popularity_fields, percentile):
    """
    Given a list of fields that occur in the `meta_data` column, return a dict
    mapping each field to its `percentile`th percentile value.
    """
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    field_queries = []
    for field in popularity_fields:
        field_queries.append(
            f"percentile_disc({percentile}) WITHIN GROUP "
            f"(ORDER BY meta_data->>'{field}') AS {field}"
        )
    select_predicate = ', '.join(field_queries)
    select = f'SELECT {select_predicate} from image'
    res = postgres.get_records(select)
    field_percentiles = {
        field: int(value) for field, value in zip(popularity_fields, res[0])
    }
    return field_percentiles


def build_popularity_dump_query(popularity_fields):
    """
    Given a list of fields used in popularity data calculations, build a query
    returning all rows with at least one popularity metric.
    """
    # SELECT predicate for each popularity field
    selection_qs = []
    # WHERE predicate excluding null values for each field
    field_not_null_qs = []
    for field in popularity_fields:
        selection_qs.append(f"meta_data->>'{field}' AS {field}")
        field_not_null_qs.append(f"meta_data->>'{field}' IS NOT NULL")
    selections = ', '.join(selection_qs)
    field_not_null = ' OR '.join(field_not_null_qs)
    return f"SELECT identifier, provider, {selections} FROM image " \
           f"WHERE ({field_not_null})"


def dump_selection_to_tsv(postgres_conn_id, query, tsv_file_name):
    postgres = PostgresHook(postgres_conn_id=postgres_conn_id)
    query = dedent(
        f"COPY ({query}) TO STDOUT "
        f"WITH CSV HEADER DELIMITER E'\t'"
    )
    postgres.copy_expert(query, tsv_file_name)
