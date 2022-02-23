from common.loader import paths, s3, sql
from common.loader.paths import _extract_media_type


def copy_to_s3(output_dir, bucket, identifier, aws_conn_id):
    tsv_file_name = paths.get_staged_file(output_dir, identifier)
    media_type = _extract_media_type(tsv_file_name)
    s3.copy_file_to_s3_staging(
        identifier, tsv_file_name, bucket, aws_conn_id, media_prefix=media_type
    )


def load_s3_data(
    bucket,
    aws_conn_id,
    postgres_conn_id,
    identifier,
    ti,
):
    media_type = ti.xcom_pull(task_ids="stage_oldest_tsv_file", key="media_type")
    tsv_version = ti.xcom_pull(task_ids="stage_oldest_tsv_file", key="tsv_version")

    if media_type is None:
        media_type = "image"
    tsv_key = s3.get_staged_s3_object(
        identifier, bucket, aws_conn_id, media_prefix=media_type
    )
    sql.load_s3_data_to_intermediate_table(
        postgres_conn_id, bucket, tsv_key, identifier, media_type
    )
    sql.upsert_records_to_db_table(
        postgres_conn_id, identifier, media_type=media_type, tsv_version=tsv_version
    )


def load_from_s3(
    bucket,
    key,
    postgres_conn_id,
    media_type,
    tsv_version,
    identifier,
):
    sql.load_s3_data_to_intermediate_table(
        postgres_conn_id, bucket, key, identifier, media_type
    )
    # Returns record count
    return sql.upsert_records_to_db_table(
        postgres_conn_id, identifier, media_type=media_type, tsv_version=tsv_version
    )
