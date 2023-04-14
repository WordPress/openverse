def expire_old_images(
    postgres_conn_id,
    provider,
    image_table=TABLE_NAMES[IMAGE],
    task: AbstractOperator = None,
):
    postgres = PostgresHook(
        postgres_conn_id=postgres_conn_id,
        default_statement_timeout=PostgresHook.get_execution_timeout(task),
    )

    if provider not in OLDEST_PER_PROVIDER:
        raise Exception(
            f"Provider value {provider} not defined in the "
            f"OLDEST_PER_PROVIDER dictionary"
        )

    """
    Select all records that are outdated
    """
    select_query = dedent(
        f"""
        SELECT {col.FOREIGN_ID.db_name}
        FROM {image_table}
        WHERE
        {col.PROVIDER.db_name} = '{provider}'
        AND
        {col.UPDATED_ON.db_name} < {NOW} - INTERVAL '{OLDEST_PER_PROVIDER[provider]}';
        """
    )

    selected_records = postgres.get_records(select_query)

    """
    Set the 'removed_from_source' value of each selected row to True to
    indicate that those images are outdated
    """
    for row in selected_records:
        foreign_id = row[0]

        postgres.run(
            dedent(
                f"""
                UPDATE {image_table}
                SET {col.REMOVED.db_name} = 't'
                WHERE
                {image_table}.{col.PROVIDER.db_name} = '{provider}'
                AND
                MD5({image_table}.{col.FOREIGN_ID.db_name}) = MD5('{foreign_id}');
                """
            )
        )
