from psycopg2.sql import SQL, Identifier, Literal


def get_existence_queries(model_name: str, table_name: str) -> tuple[SQL, SQL]:
    """
    Get the query for checking whether a media is deleted or mature.

    Returns two SQL queries for checking if an identifier exists in the deleted or the
    mature tables for the media respectively. The media tables are assumed to be named
    with the prefixes "api_deleted" and "api_mature" respectively.

    Required Arguments:

    model_name: the name to use for the deleted and mature tables
    table_name: the name of the media table to check entries in
    """
    exists_in_table = (
        "EXISTS(SELECT 1 FROM {table} " "WHERE identifier = {identifier}) AS {name}"
    )
    exists_in_deleted_table = SQL(exists_in_table).format(
        table=Identifier(f"api_deleted{model_name}"),
        identifier=Identifier(table_name, "identifier"),
        name=Identifier("deleted"),
    )
    exists_in_mature_table = SQL(exists_in_table).format(
        table=Identifier(f"api_mature{model_name}"),
        identifier=Identifier(table_name, "identifier"),
        name=Identifier("mature"),
    )
    return exists_in_deleted_table, exists_in_mature_table


def get_reindex_query(
    model_name: str, table_name: str, start_id: int, end_id: int
) -> SQL:
    deleted, mature = get_existence_queries(model_name, table_name)

    return SQL(
        "SELECT *, {deleted}, {mature} "
        "FROM {table_name} "
        "WHERE id BETWEEN {start_id} AND {end_id};"
    ).format(
        deleted=deleted,
        mature=mature,
        table_name=Identifier(table_name),
        start_id=Literal(start_id),
        end_id=Literal(end_id),
    )
