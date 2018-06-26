import subprocess
import unittest
import os
import es_syncer.sync
import pdb

from subprocess import DEVNULL
from elasticsearch_dsl import Search, connections

this_dir = os.path.dirname(__file__)


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
            .ElasticsearchSyncer(self.db_conn, self.es, 'public.image')

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
            pdb.set_trace()
            # extra ceremony required to properly escape jsonb CSV dumps
            db_curr\
                .copy_expert(
                    """
                    COPY public.image FROM '/mock_data/mocked_images.csv'
                    WITH (FORMAT CSV, DELIMITER ',', QUOTE '"')
                    """, mockfile)
            self.db_conn.commit()

        db_curr = self.db_conn.cursor()
        db_curr.execute('select count(*) from public.image;')
        num_images = db_curr.fetchone()[0]

        s = Search(index='public.image')
        response = s.execute()

        num_images_in_es = response.hits.total
        self.assertTrue(num_images == num_images_in_es)

    def test_indexed_correctly(self):
        """
        Check that a single document has the expected schema.
        """
        self.fail("Not implemented")


if __name__ == '__main__':
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
    subprocess.Popen(start_cmd, shell=True, stdout=DEVNULL)

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
    subprocess.call(stop_cmd, shell=True, stdout=DEVNULL)