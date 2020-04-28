import logging
import os

from airflow.hooks.S3_hook import S3Hook

logger = logging.getLogger(__name__)

DEFAULT_MEDIA_PREFIX = 'image'
STAGING_PREFIX = 'db_loader_staging'


def copy_file_to_s3_staging(
        identifier,
        tsv_file_path,
        aws_conn_id,
        media_prefix=DEFAULT_MEDIA_PREFIX,
        staging_prefix=STAGING_PREFIX,
        s3_bucket=None
):
    s3_bucket = s3_bucket or os.getenv('CCCATALOG_STORAGE_BUCKET')
    logger.info(f'Creating staging object in s3_bucket:  {s3_bucket}')
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    file_name = os.path.split(tsv_file_path)[1]
    staging_object_prefix = _get_staging_object_prefix(
        identifier,
        media_prefix,
        staging_prefix
    )
    staging_key = _s3_join_path(staging_object_prefix, file_name)
    s3.load_file(tsv_file_path, staging_key, bucket_name=s3_bucket)


def _get_staging_object_prefix(
        identifier,
        media_prefix,
        staging_prefix,
):
    return _s3_join_path(media_prefix, staging_prefix, identifier)


def _s3_join_path(*args):
    return '/'.join(
        [s.strip('/') for s in args]
    )
