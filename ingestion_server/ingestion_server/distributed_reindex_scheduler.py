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
import socket
from ingestion_server.state import register_indexing_job


client = boto3.client('ec2', region_name=os.getenv('AWS_REGION', 'us-east-1'))


def schedule_distributed_index(db_conn, target_index):
    workers = _prepare_workers()
    registered = register_indexing_job(workers, target_index)
    if registered:
        _assign_work(db_conn, workers, target_index)


def _assign_work(db_conn, workers, target_index):
    est_records_query = 'SELECT id FROM image ORDER BY id DESC LIMIT 1'
    with db_conn.cursor() as cur:
        cur.execute(est_records_query)
        estimated_records = cur.fetchone()[0]
    records_per_worker = math.floor(estimated_records / len(workers))

    worker_url_template = 'http://{}:8002'
    # Wait for the workers to start.
    for worker in workers:
        worker_url = worker_url_template.format(worker)
        succeeded = _wait_for_healthcheck(f'{worker_url}/healthcheck')
        if not succeeded:
            return False
    for idx, worker in enumerate(workers):
        worker_url = worker_url_template.format(worker)
        params = {
            'start_id': idx * records_per_worker,
            'end_id': (1 + idx) * records_per_worker,
            'target_index': target_index
        }
        log.info(f'Assigning job {params} to {worker_url}')
        requests.post(worker_url + '/indexing_task', json=params)


def _prepare_workers():
    """
    Get a list of internal URLs bound to each indexing worker. If the worker is
    stopped, start the worker.

    :return: A list of private URLs pointing to each available indexing worker
    """
    environment = os.getenv('ENVIRONMENT', 'local')
    if environment == 'local':
        return [socket.gethostbyname('indexer-worker')]
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
        server = instance['PrivateIpAddress']
        _id = instance['InstanceId']
        servers.append(server)
        ids.append(_id)
    log.info(f'Selected worker instances {servers}')
    client.start_instances(InstanceIds=ids)
    return servers


def _wait_for_healthcheck(endpoint, attempts=60, wait=5):
    """
    Wait for the instance at `endpoint` to become healthy before assigning work.

    :param endpoint: The URL to test
    :param attempts: Number of attempts at reaching healthcheck
    :param wait: Amount of time to wait between each attempt
    :return: True if the healthcheck succeeded
    """
    num_attempts = 0
    healthcheck_passed = False
    while not healthcheck_passed and num_attempts < attempts:
        try:
            log.info(f'Checking {endpoint}. . .')
            response = requests.get(endpoint, timeout=3)
            if response.status_code == 200:
                healthcheck_passed = True
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(wait)
        num_attempts += 1
    if num_attempts >= attempts or not healthcheck_passed:
        log.error(f'Timed out waiting for {endpoint}.')
        return False
    else:
        log.info(f'{endpoint} passed healthcheck')
        return True
