import subprocess
import unittest
import os
import psycopg2
import requests
import logging
import time
import multiprocessing
# Q: Why yet another microframework? Why not use Falcon?
# A: This one can be easily run from within the test suite, while Falcon cannot.
from bottle import Bottle, run, HTTPResponse
from multiprocessing import Process
from subprocess import DEVNULL
from elasticsearch import Elasticsearch, RequestsHttpConnection

"""
An integration test for the Ingestion Server. Spin up Docker containers,
load 1000 images into the upstream database, and ensure that the data has been 
copied and indexed downstream.
"""

this_dir = os.path.dirname(__file__)
local_ingestion_server = 'http://localhost:60002'
ENABLE_DETAILED_LOGS = True


def _get_host_ip():
    # We need to send callbacks from the Docker network to the host machine.
    # Read the docker0 interface to figure out how to reach the host.
    ip_docker0 = subprocess.run(
        ['ip', 'addr', 'show', 'docker0'],
        stdout=subprocess.PIPE
    )
    docker0_tokens = ip_docker0.stdout.decode('utf-8').split(' ')
    inet_idx = docker0_tokens.index('inet')
    host_ip, _ = docker0_tokens[inet_idx + 1].split('/')
    return host_ip


class TestIngestion(unittest.TestCase):

    @staticmethod
    def initialize(schemaf='schema.sql'):
        """
        Wait for integration test dependencies to be started by docker-compose.
        Populate the upstream database with initial data; add the schema
        (no data) to the downstream database.
        """
        while True:
            try:
                upstream_db = psycopg2.connect(
                    dbname='openledger',
                    user='deploy',
                    port=59999,
                    password='deploy',
                    host='localhost',
                    connect_timeout=5
                )
                downstream_db = psycopg2.connect(
                    dbname='openledger',
                    user='deploy',
                    port=60000,
                    password='deploy',
                    host='localhost',
                    connect_timeout=5
                )
            except psycopg2.OperationalError as e:
                logging.debug(e)
                logging.info('Databases not ready, reconnecting. . .')
                time.sleep(5)
                continue
            logging.info('Successfully connected to databases')
            break
        mockfname = f"{this_dir}/mock_data/mocked_images.csv"
        schemafname = f"{this_dir}/mock_data/{schemaf}"
        with open(mockfname) as mockfile, open(schemafname) as schema_file:
            upstream_cur = upstream_db.cursor()
            downstream_cur = downstream_db.cursor()
            schema = schema_file.read()
            upstream_cur.execute(schema)
            downstream_cur.execute(schema)
            downstream_db.commit()
            upstream_db.commit()
            upstream_cur.copy_expert(
                """
                COPY image FROM '/mock_data/mocked_images.csv'
                WITH (FORMAT CSV, DELIMITER ',', QUOTE '"')
                """, mockfile)
            upstream_db.commit()
            downstream_cur.close()
            upstream_cur.close()
            upstream_db.close()
            downstream_db.close()
        # Wait for ingestion server and Elasticsearch to come up.
        ready_stats = {'yellow', 'green'}
        max_attempts = 10
        attempts = 0
        while True:
            try:
                _ = requests.get('http://localhost:60002')
                es_res = requests.get('http://localhost:60001/_cluster/health')
                res_json = es_res.json()
                if res_json['status'] not in ready_stats:
                    continue
            except requests.exceptions.ConnectionError:
                if attempts > max_attempts:
                    logging.error('Ingestion server timed out. Giving up.')
                    return False
                logging.info('Waiting for ingestion server to come up...')
                time.sleep(5)
                continue
            finally:
                attempts += 1
            logging.info('Successfully connected to ingestion server')
            break

    @staticmethod
    def clean_up():
        upstream_db = psycopg2.connect(
            dbname='openledger',
            user='deploy',
            port=59999,
            password='deploy',
            host='localhost',
            connect_timeout=5
        )
        downstream_db = psycopg2.connect(
            dbname='openledger',
            user='deploy',
            port=60000,
            password='deploy',
            host='localhost',
            connect_timeout=5
        )
        with upstream_db.cursor() as upstream_cur, \
                downstream_db.cursor() as downstream_cur:
            cleanup = 'DROP TABLE image CASCADE'
            upstream_cur.execute(cleanup)
            downstream_cur.execute(cleanup)
        upstream_db.commit()
        downstream_db.commit()
        upstream_db.close()
        downstream_db.close()

    def _wait_for_callback(self, endpoint_name="/task_done"):
        """
        Block until a callback arrives. Time out if it doesn't arrive within
        10 seconds.
        :param endpoint_name:
        :return:
        """
        callback_listener = Bottle()
        # Signal when a callback has been received
        callback_received = multiprocessing.Value('i', 0)

        @callback_listener.route(endpoint_name, method="post")
        def handle_task_callback():
            callback_received.value = 1
            return HTTPResponse(status=204)

        kwargs = {
            'host': _get_host_ip(),
            'port': 58000,
            'quiet': (not ENABLE_DETAILED_LOGS)
        }
        cb_listener_process = Process(
            target=run,
            args=(callback_listener,),
            kwargs=kwargs
        )
        cb_listener_process.start()
        timeout_seconds = 10
        poll_time = 0.1
        running_time = 0
        while callback_received.value != 1:
            running_time += poll_time
            time.sleep(poll_time)
            if running_time >= timeout_seconds:
                cb_listener_process.terminate()
                self.fail('Timed out waiting for task callback.')
        cb_listener_process.terminate()

    def test01_list_tasks_empty(self):
        resp = requests.get('http://localhost:60002/task')
        resp_json = resp.json()
        msg = 'There should be no tasks in the task list'
        self.assertEqual(resp_json, [], msg)

    def test02_ingest_succeeds(self):
        """
        Check that INGEST_UPSTREAM task completes successfully and responds
        with a callback.
        """
        req = {
            'model': 'image',
            'action': 'INGEST_UPSTREAM',
            'callback_url': f'http://{_get_host_ip()}:58000/task_done'
        }
        res = requests.post('http://localhost:60002/task', json=req)
        stat_msg = "The job should launch successfully and return 202 ACCEPTED."
        self.assertEqual(res.status_code, 202, msg=stat_msg)
        # Wait for the task to send us a callback.
        self._wait_for_callback('/task_done')

        return True

    def test03_upstream_indexed(self):
        """
        Check that the data has been successfully indexed in Elasticsearch.
        """
        es = Elasticsearch(
            host='localhost',
            port=60001,
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=10,
            retry_on_timeout=True,
            http_auth=None,
            wait_for_status='yellow'
        )
        es_query = {
            "query": {
                "match_all": {}
            }
        }
        es.indices.refresh(index='image')
        search_response = es.search(
            index="image",
            body=es_query
        )
        msg = 'There should be 1000 documents in Elasticsearch after ingestion.'
        self.assertEquals(search_response['hits']['total'], 1000, msg)

    def test04_last_task_in_status_list(self):
        resp = requests.get('http://localhost:60002/task')
        resp_json = resp.json()
        msg = 'There should be one task in the task list now.'
        self.assertEqual(1, len(resp_json), msg)

    def test05_removed_from_source_not_indexed(self):
        id_to_check = 10494466  # Index for which we changed manually False to True
        es = Elasticsearch(
            host='localhost',
            port=60001,
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=10,
            retry_on_timeout=True,
            http_auth=None,
            wait_for_status='yellow'
        )
        es_query = {
            "query": {
                "match": {
                    "_id": id_to_check
                }
            }
        }
        es.indices.refresh(index='image')
        search_response = es.search(
            index="image",
            body=es_query
        )

        num_hits = search_response['hits']['total']
        msg = f"id {id_to_check} should not show up in search results."
        self.assertEqual(0, num_hits, msg)


if __name__ == '__main__':
    log_level = logging.INFO if ENABLE_DETAILED_LOGS else logging.CRITICAL
    logging.basicConfig(level=log_level)
    docker_stdout = None if ENABLE_DETAILED_LOGS else DEVNULL

    # Generate an up-to-date docker-compose integration test file.
    return_code = \
        subprocess.call('test/generate_integration_test_docker_compose.py')
    if return_code != 0:
        print('Failed to generate integration test docker-compose.'
              'The existing file on disk will be used instead.')

    # Start Elasticsearch and database.
    print('Starting integration test datastores. . .')
    integration_compose = \
        os.path.join(this_dir, 'integration-test-docker-compose.yml')
    start_cmd = f'docker-compose -f {integration_compose} up --build'
    subprocess.Popen(start_cmd, shell=True, stdout=docker_stdout)

    # Run tests.
    try:
        print('Beginning tests')
        TestIngestion.initialize()
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIngestion)
        unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        # Stop Elasticsearch and database. Delete attached volumes.
        TestIngestion.clean_up()
        stop_cmd = f'docker-compose -f {integration_compose} down -v'
        subprocess.call(stop_cmd, shell=True, stdout=docker_stdout)
