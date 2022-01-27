import boto3
import pytest

from tests.dags.common.loader.test_s3 import ACCESS_KEY, S3_LOCAL_ENDPOINT, SECRET_KEY


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

    def _delete_all_objects():
        key_list = [{"Key": obj.key} for obj in bucket.objects.all()]
        if len(list(bucket.objects.all())) > 0:
            bucket.delete_objects(Delete={"Objects": key_list})

    if bucket.creation_date:
        _delete_all_objects()
    else:
        bucket.create()
    yield bucket
    _delete_all_objects()


@pytest.fixture
def identifier(request):
    return f"{hash(request.node.name)}".replace("-", "_")


@pytest.fixture
def image_table(identifier):
    # Parallelized tests need to use distinct database tables
    return f"image_{identifier}"
