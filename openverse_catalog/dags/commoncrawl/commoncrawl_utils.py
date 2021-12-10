from airflow.providers.amazon.aws.hooks.s3 import S3Hook


def load_file_to_s3(local_file, remote_key, bucket, aws_conn_id):
    s3 = S3Hook(aws_conn_id=aws_conn_id)
    s3.load_file(local_file, remote_key, replace=True, bucket_name=bucket)


def get_load_s3_task_id(s3_key: str) -> str:
    return f"load_{s3_key.replace('/', '_').replace('.', '_')}_to_s3"
