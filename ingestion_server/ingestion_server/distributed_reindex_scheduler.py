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
from boto3 import ec2


def schedule_distributed_index(db_conn):
    _start_workers()
    _assign_work(db_conn)


def _assign_work(db_conn, workers):
    est_records_query = "SELECT n_live_tup" \
                        "  FROM pg_stat_all_tables" \
                        "  WHERE relname='image';"
    with db_conn.cursor() as cur:
        cur.execute(est_records_query)
        estimated_records = cur.fetchone()[0]
    records_per_worker = math.floor(estimated_records / len(workers))

    for worker in workers:
        print(worker)


def _start_workers():
    servers = []
    return servers


