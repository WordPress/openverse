from psycopg2.sql import SQL, Identifier


# from ingestion_server.constants.internal_types import ApproachType


def get_existence_queries(model: str, table: str = None) -> tuple[SQL, SQL]:
    """
    Get the query for checking whether a media is deleted or mature.

    Returns two SQL queries for checking if an identifier exists in the deleted or the
    mature tables for the media respectively. The media tables are assumed to be named
    with the prefixes "api_deleted" and "api_mature" respectively.

    :param model: the name to use for the deleted and mature tables
    :param table: the name of the media table to check entries in
    :return: the queries to check if for presence in the deleted/mature table
    """

    if not table:
        table = model  # By default, tables are named after the model.

    exists_in_table = (
        "EXISTS(SELECT 1 FROM {table} " "WHERE identifier = {identifier}) AS {name}"
    )
    exists_in_deleted_table = SQL(exists_in_table).format(
        table=Identifier(f"api_deleted{model}"),
        identifier=Identifier(table, "identifier"),
        name=Identifier("deleted"),
    )
    exists_in_mature_table = SQL(exists_in_table).format(
        table=Identifier(f"api_mature{model}"),
        identifier=Identifier(table, "identifier"),
        name=Identifier("mature"),
    )
    return exists_in_deleted_table, exists_in_mature_table
