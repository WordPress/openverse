"""
Allocate hardware for performing a distributed index by spawning several
indexer_worker instances on multiple machines. Then, partition the work across
each worker, notifying each worker which partition to reindex through an HTTP
request.

Once the reindexing job is finished, each worker will notify Ingestion Server
and self destruct.
"""
from boto3 import ec2


def schedule_distributed_crawl():
    _start_workers()


def _start_workers():
    servers = []
    return servers

