"""
Allocate hardware for performing a distributed index by spawning several
indexer_worker instances on multiple machines. Then, partition the work across
each worker, notifying each worker which partition to reindex through an HTTP
request.

Once the reindexing job is finished, each worker will notify Ingestion Server
and self destruct.
"""
import math
import requests
import pprint
import logging as log
from boto3 import ec2


def schedule_distributed_index(db_conn):
    _start_workers()
    _assign_work(db_conn, ['foo'])


def _assign_work(db_conn, workers):
    est_records_query = "SELECT n_live_tup" \
                        "  FROM pg_stat_all_tables" \
                        "  WHERE relname='image';"
    with db_conn.cursor() as cur:
        cur.execute(est_records_query)
        estimated_records = cur.fetchone()[0]
    records_per_worker = math.floor(estimated_records / len(workers))

    for idx, worker in enumerate(workers):
        worker_url = 'http://indexer-worker:8002/indexing_task'
        params = {
            'start_id': idx * records_per_worker,
            'end_id': (1 + idx) * records_per_worker,
            'target_index': 'distributed-indexing-test'
        }
        log.info(pprint.pprint(params))
        requests.post(worker_url, json=params)


def _start_workers():
    servers = []
    return servers


