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
from bottle import Bottle, run, request, route, HTTPResponse
from multiprocessing import Process
from subprocess import DEVNULL

this_dir = os.path.dirname(__file__)
ENABLE_DETAILED_LOGS = False

# Signal when a task has finished.
callback_received = multiprocessing.Value('i', 0)


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

    def setUp(self):
        """
        Wait for integration test dependencies to be started by docker-compose.
        Populate the upstream database with initial data; add the schema
        (no data) to the downstream database.
        """
        super().setUp()
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
        self.upstream_con = upstream_db
        self.downstream_con = downstream_db
        with open(this_dir + "/mock_data/mocked_images.csv") as mockfile,\
                open(this_dir + "/mock_data/schema.sql") as schema_file:
            upstream_cur = upstream_db.cursor()
            downstream_cur = downstream_db.cursor()
            schema = schema_file.read()
            upstream_cur.execute(schema)
            downstream_cur.execute(schema)
            downstream_db.commit()
            upstream_db.commit()
            upstream_cur\
                .copy_expert(
                    """
                    COPY image FROM '/mock_data/mocked_images.csv'
                    WITH (FORMAT CSV, DELIMITER ',', QUOTE '"')
                    """, mockfile)
            upstream_db.commit()
            downstream_cur.close()
            upstream_cur.close()
            upstream_db.close()
            downstream_db.close()
        # Wait for ingestion server to come up.
        max_attempts = 15
        attempts = 0
        while True:
            try:
                _ = requests.get('http://localhost:60002')
                attempts += 1
            except requests.exceptions.ConnectionError:
                if attempts > max_attempts:
                    logging.error('Integration server timed out. Giving up.')
                    return False
                logging.info('Waiting for ingestion server to come up...')
                time.sleep(5)
                continue
            logging.info('Successfully connected to ingestion server')
            break

    def tearDown(self):
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
        Block until a callback arrives. Not thread-safe.
        :param endpoint_name:
        :return:
        """
        callback_listener = Bottle()

        @callback_listener.route(endpoint_name, method="post")
        def handle_task_callback():
            global callback_received
            callback_received.value = 1
            return HTTPResponse(status=204)

        kwargs = {
            'host': _get_host_ip(),
            'port': 58000
        }
        cb_listener_process = Process(
            target=run,
            args=(callback_listener,),
            kwargs=kwargs
        )
        cb_listener_process.start()
        timeout_seconds = 15
        poll_time = 0.1
        running_time = 0
        global callback_received
        while callback_received.value != 1:
            running_time += poll_time
            time.sleep(poll_time)
            if running_time >= timeout_seconds:
                cb_listener_process.terminate()
                self.fail('Timed out waiting for task callback.')
        cb_listener_process.terminate()

    def test_ingest_succeeds(self):
        """
        Check that INGEST_UPSTREAM task completes successfully and responds
        with a callback.
        """
        req = {
            'model': 'image',
            'action': 'INGEST_UPSTREAM',
            'callback_url': 'http://{}:58000/task_done'.format(_get_host_ip())
        }
        res = requests.post('http://localhost:60002/task', json=req)
        stat_msg = "The job should launch successfully and return 202 ACCEPTED."
        self.assertEqual(res.status_code, 202, msg=stat_msg)
        # Wait for the task to send us a callback.
        self._wait_for_callback()

        return True


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
    start_cmd = 'docker-compose -f {} up --build'\
        .format(integration_compose)
    subprocess.Popen(start_cmd, shell=True, stdout=docker_stdout)

    # Run tests.
    try:
        print('Beginning tests')
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIngestion)
        unittest.TextTestRunner(verbosity=2).run(suite)
    finally:
        # Stop Elasticsearch and database. Delete attached volumes.
        stop_cmd = 'docker-compose -f {} down -v'.format(integration_compose)
        subprocess.call(stop_cmd, shell=True, stdout=docker_stdout)
