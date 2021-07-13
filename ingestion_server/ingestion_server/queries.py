from psycopg2.sql import SQL, Identifier


def get_existence_queries(table_name):
    """
    Get the query for fetching a section of the media records to index.

    :param table_name: the name of the media table to index
    """

    exists_in_table = (
        'exists(SELECT 1 FROM {table} '
        'WHERE identifier = {identifier}) as {name}'
    )
    exists_in_deleted_table = SQL(exists_in_table).format(
        table=Identifier(f'api_deleted{table_name}'),
        identifier=Identifier(table_name, "identifier"),
        name=Identifier('deleted'),
    )
    exists_in_mature_table = SQL(exists_in_table).format(
        table=Identifier(f'api_mature{table_name}'),
        identifier=Identifier(table_name, "identifier"),
        name=Identifier('mature'),
    )
    return exists_in_deleted_table, exists_in_mature_table
