import subprocess
import unittest
import os
import psycopg2
import requests
import logging
import time
import sys
from subprocess import DEVNULL
from multiprocessing import Process
from elasticsearch_dsl import Search, connections

this_dir = os.path.dirname(__file__)
ENABLE_DETAILED_LOGS = True


def _get_host_ip():
    # We need to send callbacks from the Docker network to the host
    # machine; use the docker0 interface to do this.
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
        Populate the upstream database and wait for ingestion server to start.
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
        # Delete test data.
        with self.upstream_con.cursor() as upstream_cur,\
                self.downstream_con.cursor() as downstream_cur:
            upstream_cur.execute('DROP TABLE image CASCADE;')
            downstream_cur.execute('DROP TABLE image CASCADE;')
            self.upstream_con.commit()
            self.downstream_con.commit()

    def test_ingest(self):
        req = {
            'model': 'image',
            'action': 'INGEST_UPSTREAM',
            'callback': '{}:58000'.format(_get_host_ip())
        }
        logging.info('Sending request to ingestion server')
        res = requests.post('http://localhost:60002/task', json=req)
        self.assertEqual(res.status_code, 200)
        return True

    def test_downstream_consistency(self):
        return False


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
