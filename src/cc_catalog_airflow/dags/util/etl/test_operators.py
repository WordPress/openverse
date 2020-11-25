from unittest.mock import patch

from util.etl import operators


def test_load_file_to_s3_uses_connection_id():
    local_file = "/test/file/here.txt"
    remote_key = "abc/def/here.txt"
    aws_conn_id = "test_conn_id"
    test_bucket_name = "test-bucket"

    with patch.object(operators, "S3Hook") as mock_s3:
        operators._load_file_to_s3(
            local_file,
            remote_key,
            test_bucket_name,
            aws_conn_id,
        )
    mock_s3.assert_called_once_with(aws_conn_id=aws_conn_id)


def test_load_file_to_s3_loads_file():
    local_file = "/test/file/here.txt"
    remote_key = "abc/def/here.txt"
    aws_conn_id = "test_conn_id"
    test_bucket_name = "test-bucket"

    with patch.object(operators.S3Hook, "load_file") as mock_s3_load_file:
        operators._load_file_to_s3(
            local_file,
            remote_key,
            test_bucket_name,
            aws_conn_id,
        )
    mock_s3_load_file.assert_called_once_with(
        local_file,
        remote_key,
        replace=True,
        bucket_name=test_bucket_name,
    )


def test_get_task_return_value_template():
    expect_template_string = (
        "{{ task_instance.xcom_pull(task_ids='abc123', key='return_value') }}"
    )
    actual_string = operators._get_task_return_value_template("abc123")
    assert actual_string == expect_template_string
