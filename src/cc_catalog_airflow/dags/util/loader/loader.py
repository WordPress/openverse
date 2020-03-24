from util.loader import paths, sql


def load_data(output_dir, postgres_conn_id, identifier):
    tsv_file_name = paths.get_staged_file(output_dir, identifier)
    sql.import_data_to_intermediate_table(
        postgres_conn_id,
        tsv_file_name,
        identifier
    )
    sql.upsert_records_to_image_table(postgres_conn_id, identifier)
