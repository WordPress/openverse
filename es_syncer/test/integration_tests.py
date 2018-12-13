import subprocess
import unittest
import os

import es_syncer.indexer
import logging
from subprocess import DEVNULL
from multiprocessing import Process
from elasticsearch_dsl import Search, connections

this_dir = os.path.dirname(__file__)
ENABLE_DETAILED_LOGS = True


class TestReplication(unittest.TestCase):

    def setUp(self):
        super().setUp()
        # Configure synchronizer
        es_syncer.indexer.DATABASE_HOST = 'localhost'
        es_syncer.indexer.DATABASE_PORT = 60000
        es_syncer.indexer.DATABASE_NAME = 'openledger'
        es_syncer.indexer.DATABASE_PASSWORD = 'deploy'
        es_syncer.indexer.DATABASE_USER = 'deploy'
        es_syncer.indexer.ELASTICSEARCH_PORT = 60001
        es_syncer.indexer.ELASTICSEARCH_URL = 'localhost'
        es_syncer.indexer.DB_BUFFER_SIZE = 100000
        print('Waiting for Elasticsearch to start. . .')
        self.es = es_syncer.indexer.elasticsearch_connect()
        connections.connections.add_connection('default', self.es)
        # DB connection used by synchronizer
        self.db_conn = \
            es_syncer.indexer.database_connect()
        # DB connection used to write mock data by this integration test
        self.write_db_conn = \
            es_syncer.indexer.database_connect()
        self.syncer = es_syncer.indexer.TableIndexer(self.es, ['image'])

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
            db_curr = self.write_db_conn.cursor()
            schema = schema_file.read()
            db_curr.execute(schema)
            self.write_db_conn.commit()
            db_curr\
                .copy_expert(
                    """
                    COPY image FROM '/mock_data/mocked_images.csv'
                    WITH (FORMAT CSV, DELIMITER ',', QUOTE '"')
                    """, mockfile)
            self.write_db_conn.commit()

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
        es_doc_count = s.count()

        self.assertTrue(expected_doc_count <= es_doc_count,
                        'There should be at least as many documents in'
                        ' Elasticsearch as records Postgres.')


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
