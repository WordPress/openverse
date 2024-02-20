import logging
import os
from pathlib import Path

from airflow.exceptions import AirflowSkipException
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from common.loader import paths


logger = logging.getLogger(__name__)

DEFAULT_MEDIA_PREFIX = "image"
STAGING_PREFIX = "db_loader_staging"


def copy_file_to_s3_staging(
    identifier,
    tsv_file_path,
    s3_bucket,
    aws_conn_id,
    media_prefix=DEFAULT_MEDIA_PREFIX,
    staging_prefix=STAGING_PREFIX,
):
    """
    Copy a media file from the staging directory, using a media, staging,
    and identifiers to construct the S3 key.
    """
    logger.info(f"Creating staging object in s3_bucket:  {s3_bucket}")
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    file_name = os.path.split(tsv_file_path)[1]
    staging_object_prefix = _get_staging_object_prefix(
        identifier, media_prefix, staging_prefix
    )
    staging_key = _s3_join_path(staging_object_prefix, file_name)
    s3.load_file(tsv_file_path, staging_key, bucket_name=s3_bucket)


def copy_file_to_s3(
    tsv_file_path,
    s3_bucket,
    s3_prefix,
    aws_conn_id,
    ti,
    extra_args=None,
):
    """
    Copy a TSV file to S3 with the given prefix.
    The TSV's version is pushed to the `tsv_version` XCom, and the constructed
    S3 key is pushed to the `s3_key` XCom.
    The TSV is removed after the upload is complete.

    ``extra_args`` refers to the S3Hook argument.
    """
    if tsv_file_path is None:
        raise FileNotFoundError("No TSV file path was provided")
    tsv_file = Path(tsv_file_path)
    if not tsv_file.exists():
        raise AirflowSkipException(f"TSV file {tsv_file} does not exist.")
    tsv_version = paths.get_tsv_version(tsv_file_path)
    s3_key = f"{s3_prefix}/{tsv_file.name}"
    logger.info(f"Uploading {tsv_file_path} to {s3_bucket}:{s3_key}")
    s3 = S3Hook(
        aws_conn_id=aws_conn_id,
        extra_args=extra_args or {},
    )
    s3.load_file(tsv_file_path, s3_key, bucket_name=s3_bucket)
    ti.xcom_push(key="tsv_version", value=tsv_version)
    ti.xcom_push(key="s3_key", value=s3_key)
    tsv_file.unlink()


def get_staged_s3_object(
    identifier,
    s3_bucket,
    aws_conn_id,
    media_prefix=DEFAULT_MEDIA_PREFIX,
    staging_prefix=STAGING_PREFIX,
):
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    staging_object_prefix = _get_staging_object_prefix(
        identifier, media_prefix, staging_prefix
    )
    key_list = s3.list_keys(s3_bucket, prefix=staging_object_prefix)
    assert len(key_list) == 1
    return key_list[0]


def _get_staging_object_prefix(
    identifier,
    media_prefix,
    staging_prefix,
):
    return _s3_join_path(media_prefix, staging_prefix, identifier)


def _s3_join_path(*args):
    return "/".join([s.strip("/") for s in args])
