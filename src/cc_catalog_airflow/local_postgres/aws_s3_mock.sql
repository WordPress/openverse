CREATE SCHEMA IF NOT EXISTS aws_s3;
CREATE EXTENSION plpython3u;

CREATE OR REPLACE FUNCTION aws_s3.table_import_from_s3 (
  table_name text,
  column_list text,
  options text,
  bucket text,
  file_path text,
  region text
) RETURNS int
LANGUAGE plpython3u
AS $$
    import os
    import boto3
    s3_obj = boto3.resource(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY', 'test_key'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY', 'test_secret'),
        region_name=region,
        endpoint_url=os.getenv('S3_LOCAL_ENDPOINT', 'http://s3:5000')
    ).Object(bucket, file_path)
    temp_location = '/tmp/postgres_loading.tsv'
    s3_obj.download_file(temp_location)
    with open(temp_location) as f:
        columns = '({})'.format(column_list) if column_list else ''
        res = plpy.execute(
            'COPY {} {} FROM {} {};'.format(
                table_name,
                columns,
                plpy.quote_literal(temp_location),
                options
            )
        )
    os.remove(temp_location)
    return res.nrows()
$$;
