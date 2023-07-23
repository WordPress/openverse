"""
A single worker responsible for indexing a subset of the records stored in the database.

Accept an HTTP request specifying a range of image IDs to reindex. After the
data has been indexed, notify Ingestion Server and stop the instance.
"""

import logging as log
from multiprocessing import Process

import boto3
import falcon
import requests
from decouple import config
from psycopg2.sql import SQL, Identifier, Literal

from ingestion_server import slack
from ingestion_server.es_helpers import elasticsearch_connect
from ingestion_server.indexer import TableIndexer
from ingestion_server.queries import get_existence_queries


ec2_client = boto3.client(
    "ec2",
    region_name=config("AWS_REGION", default="us-east-1"),
    aws_access_key_id=config("AWS_ACCESS_KEY_ID", default=None),
    aws_secret_access_key=config("AWS_SECRET_ACCESS_KEY", default=None),
)


class IndexingJobResource:
    def on_post(self, req, resp):
        j = req.media
        model_name = j["model_name"]
        table_name = j["table_name"]
        start_id = j["start_id"]
        end_id = j["end_id"]
        target_index = j["target_index"]
        notify_url = f"http://{req.remote_addr}:8001/worker_finished"
        _execute_indexing_task(
            model_name, table_name, target_index, start_id, end_id, notify_url
        )
        log.info(f"Received indexing request for records {start_id}-{end_id}")
        resp.status = falcon.HTTP_201


class HealthcheckResource:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


def _execute_indexing_task(
    model_name, table_name, target_index, start_id, end_id, notify_url
):
    elasticsearch = elasticsearch_connect()

    deleted, mature = get_existence_queries(model_name, table_name)
    query = SQL(
        "SELECT *, {deleted}, {mature} "
        "FROM {table_name} "
        "WHERE id BETWEEN {start_id} AND {end_id};"
    ).format(
        deleted=deleted,
        mature=mature,
        table_name=Identifier(table_name),
        start_id=Literal(start_id),
        end_id=Literal(end_id),
    )
    log.info(f"Querying {query}")
    indexer = TableIndexer(elasticsearch)
    p = Process(
        target=_launch_reindex,
        args=(model_name, table_name, target_index, query, indexer, notify_url),
    )
    p.start()
    log.info("Started indexing task")


def _launch_reindex(model, table, target_index, query, indexer, notify_url):
    worker_error = False
    try:
        indexer.replicate(model, table, target_index, query)
    except Exception as err:
        exception_type = f"{err.__class__.__module__}.{err.__class__.__name__}"
        slack.error(
            f":x_red: Error in worker while reindexing `{target_index}`"
            f"(`{exception_type}`): \n"
            f"```\n{err}\n```"
        )
        log.error("Indexing error occurred: ", exc_info=True)
        worker_error = True

    log.info(f"Notifying {notify_url}")
    requests.post(notify_url, json={"error": worker_error})
    _self_destruct()
    return


def _self_destruct():
    """Stop this EC2 instance once the task is finished."""

    # Get instance ID from AWS metadata service
    if config("ENVIRONMENT", default="local") == "local":
        log.info("Skipping self destruction because worker is in local environment")
        return
    endpoint = "http://169.254.169.254/latest/meta-data/instance-id"
    response = requests.get(endpoint)
    instance_id = response.content.decode("utf8")
    log.info("Shutting self down")
    ec2_client.stop_instances(InstanceIds=[instance_id])


api = falcon.App()
api.add_route("/indexing_task", IndexingJobResource())
api.add_route("/healthcheck", HealthcheckResource())
