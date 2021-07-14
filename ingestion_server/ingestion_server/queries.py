from psycopg2.sql import SQL, Identifier


def get_existence_queries(table):
    """
    Get the query for checking whether an identifier exists in the deleted or
    the mature tables for the media. The media tables are assumed to be named
    with the prefixes "api_deleted" and "api_mature" respectively.

    :param table: the name of the media table to check entries in
    :return: the queries to check if for presence in the deleted/mature table
    """

    exists_in_table = (
        'EXISTS(SELECT 1 FROM {table} '
        'WHERE identifier = {identifier}) AS {name}'
    )
    exists_in_deleted_table = SQL(exists_in_table).format(
        table=Identifier(f'api_deleted{table}'),
        identifier=Identifier(table, "identifier"),
        name=Identifier('deleted'),
    )
    exists_in_mature_table = SQL(exists_in_table).format(
        table=Identifier(f'api_mature{table}'),
        identifier=Identifier(table, "identifier"),
        name=Identifier('mature'),
    )
    return exists_in_deleted_table, exists_in_mature_table
