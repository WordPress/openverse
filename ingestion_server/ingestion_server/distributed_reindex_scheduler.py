"""
This module handles distributed reindexing.

Allocate hardware for performing a distributed index by spawning several
indexer_worker instances on multiple machines. Then, partition the work across
each worker, notifying each worker which partition to reindex through an HTTP
request.

Once the reindexing job is finished, each worker will notify Ingestion Server,
which should then shut down the instances.
"""

import logging as log
import math
import socket
import time

import boto3
import requests
from decouple import config

from ingestion_server.state import register_indexing_job
from ingestion_server.utils.config import get_record_limit


client = boto3.client("ec2", region_name=config("AWS_REGION", default="us-east-1"))
worker_limit = config("INDEXER_WORKER_LIMIT", default=0, cast=int)


def schedule_distributed_index(db_conn, model_name, table_name, target_index, task_id):
    workers = _prepare_workers()
    registered = register_indexing_job(workers, target_index, task_id)
    if registered:
        _assign_work(db_conn, workers, model_name, table_name, target_index)


def _assign_work(db_conn, workers, model_name, table_name, target_index):
    """Assign jobs to workers."""

    est_records_query = f"SELECT id FROM {table_name} ORDER BY id DESC LIMIT 1"
    with db_conn.cursor() as cur:
        cur.execute(est_records_query)
        estimated_records = cur.fetchone()[0]

    # If a record_limit has been set, cap the number of records to be indexed.
    if record_limit := get_record_limit():
        estimated_records = min(estimated_records, record_limit)

    records_per_worker = math.floor(estimated_records / len(workers))

    worker_url_template = "http://{}:8002"
    # Wait for the workers to start.
    failures = []
    for worker in workers:
        worker_url = worker_url_template.format(worker)
        succeeded = _wait_for_healthcheck(f"{worker_url}/healthcheck")
        if not succeeded:
            failures.append(worker)
    if failures:
        raise ValueError(
            f"Some workers didn't respond to health check: {','.join(failures)}"
        )

    for idx, worker in enumerate(workers):
        worker_url = worker_url_template.format(worker)
        params = {
            "model_name": model_name,
            "table_name": table_name,
            "start_id": idx * records_per_worker,
            "end_id": (1 + idx) * records_per_worker,
            "target_index": target_index,
        }
        log.info(f"Assigning job {params} to {worker_url}")
        requests.post(worker_url + "/indexing_task", json=params)


def _prepare_workers():
    """
    Get a list of internal URLs bound to each indexing worker.

    If the worker is stopped, start the worker.

    :return: A list of private URLs pointing to each available indexing worker
    """
    environment = config("ENVIRONMENT", default="local")
    if environment == "local":
        indexer_worker_host = config("INDEXER_WORKER_HOST", default="localhost")
        return [socket.gethostbyname(indexer_worker_host)]
    instance_filters = [
        {"Name": "tag:Name", "Values": ["indexer-worker-" + environment + "*"]},
        {"Name": "instance-state-name", "Values": ["stopped", "running"]},
    ]
    response = client.describe_instances(Filters=instance_filters)
    servers = []
    ids = []
    for reservation in response["Reservations"]:
        instance = reservation["Instances"][0]
        server = instance["PrivateIpAddress"]
        _id = instance["InstanceId"]
        servers.append(server)
        ids.append(_id)
    log.info(f"Selected worker instances {servers}")

    if worker_limit > 0:
        log.info(f"Truncating worker instances under limit {worker_limit}")
        servers = servers[:worker_limit]
        ids = ids[:worker_limit]
        log.info(f"Truncated worker instances {servers}")

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
            log.info(f"Checking {endpoint}. . .")
            response = requests.get(endpoint, timeout=3)
            if response.status_code == 200:
                healthcheck_passed = True
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(wait)
        num_attempts += 1
    if num_attempts >= attempts or not healthcheck_passed:
        log.error(f"Timed out waiting for {endpoint}.")
        return False
    else:
        log.info(f"{endpoint} passed healthcheck")
        return True
