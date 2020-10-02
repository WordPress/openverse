import logging
import sys
import time

import boto3
from botocore.httpsession import EndpointConnectionError

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__file__)

TRIES = 10
S3 = boto3.resource(
    service_name='s3',
    region_name='us-east-1',
    endpoint_url='http://localhost:5000',
    aws_access_key_id='test_key',
    aws_secret_access_key='test_secret',
)
BUCKET_NAME = 'cccatalog-storage'


def main():
    success = _create_local_s3_bucket()
    if not success:
        logger.error('Could not create bucket in local S3')
        sys.exit(1)
    else:
        sys.exit(0)


def _create_local_s3_bucket(tries=TRIES, s3=S3, bucket_name=BUCKET_NAME):
    success = False
    for i in range(1, TRIES + 1):
        try:
            logger.info(
                f'Attempting to create bucket {bucket_name}'
                ' using local s3 connection'
            )
            s3.create_bucket(Bucket=bucket_name)
            success = True
            break
        except EndpointConnectionError as conn_e:
            logger.info('S3 not yet available')
            logger.debug(f'Error was:  {conn_e}')
            logger.info(f'Waiting {i} seconds...')
            # Back off with each loop to give the S3 container a chance to
            # start.
            time.sleep(i)
    return success


if __name__ == '__main__':
    main()
