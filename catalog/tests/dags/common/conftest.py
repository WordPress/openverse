import socket
from urllib.parse import urlparse

import boto3
import pytest

from tests.dags.common.loader.test_s3 import (
    ACCESS_KEY,
    S3_LOCAL_ENDPOINT,
    SECRET_KEY,
)


POSTGRES_TEST_CONN_ID = "postgres_openledger_testing"


def _delete_bucket(bucket):
    key_list = [{"Key": obj.key} for obj in bucket.objects.all()]
    if len(list(bucket.objects.all())) > 0:
        bucket.delete_objects(Delete={"Objects": key_list})
    bucket.delete()


def pytest_configure(config):
    """
    Dynamically allow the S3 host during testing. This is required because:
    * Docker will use different internal ports depending on what's available
    * Boto3 will open a socket with the IP address directly rather than the hostname
    * We can't add the allow_hosts mark to the empty_s3_bucket fixture directly
        (see: https://github.com/pytest-dev/pytest/issues/1368)
    """
    s3_host = socket.gethostbyname(urlparse(S3_LOCAL_ENDPOINT).hostname)
    config.__socket_allow_hosts = ["s3", "postgres", s3_host]


@pytest.fixture
def empty_s3_bucket(request):
    # Bucket names can't be longer than 63 characters or have strange characters
    bucket_name = f"bucket-{hash(request.node.name)}"
    print(f"{bucket_name=}")
    bucket = boto3.resource(
        "s3",
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=S3_LOCAL_ENDPOINT,
    ).Bucket(bucket_name)

    if bucket.creation_date:
        _delete_bucket(bucket)
    bucket.create()
    yield bucket
    _delete_bucket(bucket)
