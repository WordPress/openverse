"""
Allocate hardware for performing a distributed index by spawning several
indexer_worker instances on multiple machines. Then, partition the work across
each worker, notifying each worker which partition to reindex through an HTTP
request.

Once the reindexing job is finished, each worker will notify Ingestion Server,
which should then shut down the instances.
"""
import math
import requests
import logging as log
import os
import time
import boto3


client = boto3.client(
        'ec2',
        region_name=os.getenv('AWS_REGION', 'us-east-1'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID', None),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY', None)
    )


def schedule_distributed_index(db_conn):
    workers = _prepare_workers()
    _assign_work(db_conn, workers)


def _assign_work(db_conn, workers):
    est_records_query = "SELECT n_live_tup" \
                        "  FROM pg_stat_all_tables" \
                        "  WHERE relname='image';"
    with db_conn.cursor() as cur:
        cur.execute(est_records_query)
        estimated_records = cur.fetchone()[0]
    records_per_worker = math.floor(estimated_records / len(workers))

    for idx, worker in enumerate(workers):
        worker_url = f'http://{worker}:8002'
        _wait_for_healthcheck(worker_url + '/healthcheck')
        params = {
            'start_id': idx * records_per_worker,
            'end_id': (1 + idx) * records_per_worker,
            'target_index': 'distributed-indexing-test'
        }
        requests.post(worker_url + '/indexing_task', json=params)


def _prepare_workers():
    """
    Get a list of internal URLs bound to each indexing worker. If the worker is
    stopped, start the worker.

    :return: A list of private URLs pointing to each available indexing worker
    """
    environment = os.getenv('ENVIRONMENT', 'local')
    if environment == 'local':
        return ['indexer-worker']
    instance_filters = [
        {
            'Name': 'tag:Name',
            'Values': ['indexer-worker-' + environment + '*']
        },
        {
            'Name': 'instance-state-name',
            'Values': ['stopped', 'running']
        }
    ]
    response = client.describe_instances(Filters=instance_filters)
    servers = []
    ids = []
    for reservation in response['Reservations']:
        instance = reservation['Instances'][0]
        server = instance['PrivateDnsName']
        _id = instance['InstanceId']
        servers.append(server)
        ids.append(_id)
    log.info('Selected worker instances {}'.format(servers))
    client.start_instances(InstanceIds=ids)
    return servers


def _wait_for_healthcheck(endpoint, attempts=30, wait=5):
    """
    Wait for the instance at `endpoint` to become healthy before assigning work.

    :param endpoint: The URL to test
    :param attempts: Number of attempts at reaching healthcheck
    :param wait: Amount of time to wait between each attempt
    :return:
    """
    num_attempts = 0
    healthcheck_passed = False
    while not healthcheck_passed or num_attempts < attempts:
        try:
            requests.get(endpoint)
        except requests.exceptions.RequestException:
            pass
        time.sleep(wait)
        attempts += 1
    if num_attempts >= attempts:
        log.error('Timed out waiting for indexer workers to start.')
    else:
        log.info(f'{endpoint} passed healthcheck')