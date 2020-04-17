import logging
import os

from airflow.hooks.S3_hook import S3Hook

import boto3

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
    staging_prefix = _get_staging_prefix(identifier)
    staging_key = _s3_join_path(staging_prefix, file_name)
    s3.load_file(tsv_file_path, staging_key, bucket_name=s3_bucket)


def create_staging_object(
        identifier,
        tsv_file_name,
        staging_prefix=STAGING_PREFIX,
        s3_bucket=None,
        access_key=None,
        secret_key=None,
):
    s3_bucket = s3_bucket or os.getenv('CCCATALOG_STORAGE_BUCKET')
    access_key = access_key or os.getenv('AWS_ACCESS_KEY')
    secret_key = secret_key or os.getenv('AWS_SECRET_KEY')
    logger.info(f'Creating staging object in s3_bucket:  {s3_bucket}')
    file_name = os.path.split(tsv_file_name)[1]
    s3_object_key = _s3_join_path(staging_prefix, identifier, file_name)
    logger.info(f's3_object_key:  {s3_object_key}')
    s3_object = (
        boto3
        .resource(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        .Object(s3_bucket, s3_object_key)
    )
    return s3_object


def _get_staging_prefix(
        identifier,
        media_prefix=DEFAULT_MEDIA_PREFIX,
        staging_prefix=STAGING_PREFIX,
):
    return _s3_join_path(media_prefix, staging_prefix, identifier)


def _s3_join_path(*args):
    return '/'.join(
        [s.strip('/') for s in args]
    )
