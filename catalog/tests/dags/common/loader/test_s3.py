import os
from unittest import mock

import pytest
from airflow.exceptions import AirflowSkipException
from airflow.models import TaskInstance

from common.constants import AWS_CONN_ID
from common.loader import s3


TEST_ID = "testing"
TEST_MEDIA_PREFIX = "media"
TEST_STAGING_PREFIX = "test_staging"
S3_LOCAL_ENDPOINT = os.getenv("S3_LOCAL_ENDPOINT")
S3_TEST_BUCKET = f"cccatalog-storage-{TEST_ID}"
ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
SECRET_KEY = os.getenv("AWS_SECRET_KEY")


@pytest.fixture
def mock_s3_load_file():
    with mock.patch.object(s3.S3Hook, "load_file") as load_file_mock:
        yield load_file_mock


def test_copy_file_to_s3_staging_uses_connection_id():
    identifier = TEST_ID
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    tsv_file_path = "/test/file/path/to/data.tsv"
    test_bucket_name = "test-bucket"

    with mock.patch.object(s3, "S3Hook") as mock_s3:
        s3.copy_file_to_s3_staging(
            identifier,
            tsv_file_path,
            test_bucket_name,
            AWS_CONN_ID,
            media_prefix=media_prefix,
            staging_prefix=staging_prefix,
        )
    mock_s3.assert_called_once_with(aws_conn_id=AWS_CONN_ID)


def test_copy_file_to_s3_staging_uses_bucket_environ(monkeypatch, mock_s3_load_file):
    identifier = TEST_ID
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    tsv_file_path = "/test/file/path/to/data.tsv"
    test_bucket_name = "test-bucket"
    monkeypatch.setenv("OPENVERSE_BUCKET", test_bucket_name)

    s3.copy_file_to_s3_staging(
        identifier,
        tsv_file_path,
        test_bucket_name,
        AWS_CONN_ID,
        media_prefix=media_prefix,
        staging_prefix=staging_prefix,
    )
    mock_s3_load_file.assert_called_once_with(
        tsv_file_path,
        f"{media_prefix}/{staging_prefix}/{identifier}/data.tsv",
        bucket_name=test_bucket_name,
    )


def test_copy_file_to_s3_staging_given_bucket_name():
    identifier = TEST_ID
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    tsv_file_path = "/test/file/path/to/data.tsv"
    test_bucket_name = "test-bucket-given"

    with mock.patch.object(s3.S3Hook, "load_file") as mock_s3_load_file:
        s3.copy_file_to_s3_staging(
            identifier,
            tsv_file_path,
            test_bucket_name,
            AWS_CONN_ID,
            media_prefix=media_prefix,
            staging_prefix=staging_prefix,
        )
    mock_s3_load_file.assert_called_once_with(
        tsv_file_path,
        f"{media_prefix}/{staging_prefix}/{identifier}/data.tsv",
        bucket_name=test_bucket_name,
    )


def test_get_staged_s3_object_finds_object_with_defaults(empty_s3_bucket):
    media_prefix = s3.DEFAULT_MEDIA_PREFIX
    staging_prefix = s3.STAGING_PREFIX
    identifier = TEST_ID
    file_name = "data.tsv"
    test_key = "/".join([media_prefix, staging_prefix, identifier, file_name])
    empty_s3_bucket.put_object(Key=test_key)
    actual_key = s3.get_staged_s3_object(identifier, empty_s3_bucket.name, AWS_CONN_ID)
    assert actual_key == test_key


def test_get_staged_s3_object_finds_object_with_givens(empty_s3_bucket):
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    identifier = TEST_ID
    file_name = "data.tsv"
    test_key = "/".join([media_prefix, staging_prefix, identifier, file_name])
    empty_s3_bucket.put_object(Key=test_key)
    actual_key = s3.get_staged_s3_object(
        identifier,
        empty_s3_bucket.name,
        AWS_CONN_ID,
        media_prefix=media_prefix,
        staging_prefix=staging_prefix,
    )
    assert actual_key == test_key


def test_get_staged_s3_object_complains_with_multiple_keys(empty_s3_bucket):
    media_prefix = TEST_MEDIA_PREFIX
    staging_prefix = TEST_STAGING_PREFIX
    identifier = TEST_ID
    file_1 = "data.tsv"
    file_2 = "datb.tsv"
    test_key_1 = "/".join([media_prefix, staging_prefix, identifier, file_1])
    test_key_2 = "/".join([media_prefix, staging_prefix, identifier, file_2])
    empty_s3_bucket.put_object(Key=test_key_1)
    empty_s3_bucket.put_object(Key=test_key_2)
    with pytest.raises(AssertionError):
        s3.get_staged_s3_object(
            identifier,
            empty_s3_bucket.name,
            AWS_CONN_ID,
            media_prefix=media_prefix,
            staging_prefix=staging_prefix,
        )


def test_copy_file_to_s3_no_path():
    with pytest.raises(FileNotFoundError):
        s3.copy_file_to_s3(None, "foo", "bar", "baz", None)


def test_copy_file_to_s3_no_actual_file():
    with pytest.raises(AirflowSkipException):
        s3.copy_file_to_s3("does_not_exist", "foo", "bar", "baz", None)


def test_copy_file_to_s3(tmp_path, empty_s3_bucket):
    tsv = tmp_path / "random_media_file.tsv"
    tsv.touch()
    version = "9000"
    ti_mock = mock.MagicMock(spec=TaskInstance)
    with mock.patch.object(s3.paths, "get_tsv_version", return_value=version):
        s3.copy_file_to_s3(
            tsv, empty_s3_bucket.name, "fake-prefix", AWS_CONN_ID, ti_mock
        )
    assert not tsv.exists()
    assert ti_mock.xcom_push.call_args_list == [
        mock.call(key="tsv_version", value=version),
        mock.call(key="s3_key", value="fake-prefix/random_media_file.tsv"),
    ]
    assert len(list(empty_s3_bucket.objects.all())) > 0
