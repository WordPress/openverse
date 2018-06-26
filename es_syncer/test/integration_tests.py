import subprocess
import unittest
import os
import es_syncer.sync
import time
import logging
import pdb
from subprocess import DEVNULL
from multiprocessing import Process
from elasticsearch_dsl import Search, connections

this_dir = os.path.dirname(__file__)
ENABLE_DOCKER_LOGS = False


class TestReplication(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Configure synchronizer
        es_syncer.sync.DATABASE_HOST = 'localhost'
        es_syncer.sync.DATABASE_PORT = 60000
        es_syncer.sync.DATABASE_NAME = 'openledger'
        es_syncer.sync.DATABASE_PASSWORD = 'deploy'
        es_syncer.sync.DATABASE_USER = 'deploy'
        es_syncer.sync.ELASTICSEARCH_PORT = 60001
        es_syncer.sync.ELASTICSEARCH_URL = 'localhost'
        es_syncer.sync.DB_BUFFER_SIZE = 100000
        es_syncer.sync.SYNCER_POLL_INTERVAL = 0
        print('Waiting for Elasticsearch to start. . .')
        self.es = es_syncer.sync.elasticsearch_connect()
        connections.connections.add_connection('default', self.es)
        self.db_conn = es_syncer.sync.database_connect()
        self.syncer = es_syncer.sync\
            .ElasticsearchSyncer(self.db_conn, self.es, ['image'])

    def tearDown(self):
        pass

    def test_bulk_copy(self):
        """
        Load 1000 records into Postgres. Make sure that 1000 documents end up
        in Elasticsearch.
        """
        # Add some dummy data to the database
        with open(this_dir + "/mock_data/mocked_images.csv") as mockfile,\
                open(this_dir + "/mock_data/schema.sql") as schema_file:
            db_curr = self.db_conn.cursor()
            schema = schema_file.read()
            db_curr.execute(schema)
            self.db_conn.commit()
            db_curr\
                .copy_expert(
                    """
                    COPY image FROM '/mock_data/mocked_images.csv'
                    WITH (FORMAT CSV, DELIMITER ',', QUOTE '"')
                    """, mockfile)
            self.db_conn.commit()

        # Count items we just inserted into the database
        db_curr = self.db_conn.cursor()
        db_curr.execute('select count(*) from image;')
        expected_doc_count = db_curr.fetchone()[0]

        # Synchronize with a 100ms poll interval. Give it 10 seconds to sync.
        print('Starting synchronizer')
        syncer_proc = Process(target=self.syncer.listen, args=(0.1,))
        syncer_proc.start()
        syncer_proc.join(timeout=10)
        syncer_proc.terminate()
        print('Syncing finished. Checking doc count.')

        s = Search(index='image')
        res = s.execute()
        es_doc_count = res.hits.total

        self.assertEqual(expected_doc_count, es_doc_count,
                        'There should be as many documents in Elasticsearch '
                        'as records Postgres.')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    docker_stdout = None if ENABLE_DOCKER_LOGS else DEVNULL

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
    start_cmd = 'docker-compose -f {} up'\
        .format(integration_compose)
    subprocess.Popen(start_cmd, shell=True, stdout=docker_stdout)

    # Run tests.
    try:
        print('Beginning tests')
        suite = unittest.TestLoader().loadTestsFromTestCase(TestReplication)
        unittest.TextTestRunner(verbosity=2).run(suite)
    except Exception:
        # Always continue, even if the tests fail, so we can shut down the
        # integration test containers.
        pass

    # Stop Elasticsearch and database. Delete attached volumes.
    stop_cmd = 'docker-compose -f {} down -v'.format(integration_compose)
    subprocess.call(stop_cmd, shell=True, stdout=docker_stdout)