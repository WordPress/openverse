import os
from unittest.mock import patch

import boto3

from util.loader import s3

TEST_ID = 'testing'
TEST_MEDIA_PREFIX = 'media'
TEST_STAGING_PREFIX = 'test_staging'
AWS_CONN_ID = os.getenv('AWS_TEST_CONN_ID')


def test_copy_file_to_s3_staging_uses_connection_id():
    identifier = TEST_ID
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    tsv_file_path = '/test/file/path/to/data.tsv'
    aws_conn_id = 'test_conn_id'

    with patch.object(s3, 'S3Hook') as mock_s3:
        s3.copy_file_to_s3_staging(
            identifier,
            tsv_file_path,
            aws_conn_id,
            media_prefix=media_prefix,
            staging_prefix=staging_prefix
        )
    mock_s3.assert_called_once_with(aws_conn_id=aws_conn_id)


def test_copy_file_to_s3_staging_uses_bucket_environ(monkeypatch):
    identifier = TEST_ID
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    tsv_file_path = '/test/file/path/to/data.tsv'
    aws_conn_id = 'test_conn_id'
    test_bucket_name = 'test-bucket'
    monkeypatch.setenv('CCCATALOG_STORAGE_BUCKET', test_bucket_name)

    with patch.object(
            s3.S3Hook,
            'load_file'
    ) as mock_s3_load_file:
        s3.copy_file_to_s3_staging(
            identifier,
            tsv_file_path,
            aws_conn_id,
            media_prefix=media_prefix,
            staging_prefix=staging_prefix
        )
    mock_s3_load_file.assert_called_once_with(
        tsv_file_path,
        f'{media_prefix}/{staging_prefix}/{identifier}/data.tsv',
        bucket_name=test_bucket_name
    )


def test_copy_file_to_s3_staging_given_bucket_name(monkeypatch):
    identifier = TEST_ID
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    tsv_file_path = '/test/file/path/to/data.tsv'
    aws_conn_id = 'test_conn_id'
    test_bucket_env = 'test-bucket'
    monkeypatch.setenv('CCCATALOG_STORAGE_BUCKET', test_bucket_env)
    test_bucket_name = 'test-bucket-given'

    with patch.object(
            s3.S3Hook,
            'load_file'
    ) as mock_s3_load_file:
        s3.copy_file_to_s3_staging(
            identifier,
            tsv_file_path,
            aws_conn_id,
            media_prefix=media_prefix,
            staging_prefix=staging_prefix,
            s3_bucket=test_bucket_name
        )
    print(mock_s3_load_file.mock_calls)
    print(mock_s3_load_file.method_calls)
    mock_s3_load_file.assert_called_once_with(
        tsv_file_path,
        f'{media_prefix}/{staging_prefix}/{identifier}/data.tsv',
        bucket_name=test_bucket_name
    )
