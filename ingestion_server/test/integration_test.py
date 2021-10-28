"""
Integration test for the ingestion-server. Spins up Docker containers, loads
1000 images into the upstream database, and ensures that the data has been
copied and indexed downstream.
"""

import logging
import pathlib
import platform
import subprocess
import time
import unittest
from multiprocessing import Process, Queue

import psycopg2
import pytest
import requests

# Uses Bottle because, unlike Falcon, it can be run from within the test suite.
from bottle import Bottle
from elasticsearch import Elasticsearch, RequestsHttpConnection

from .gen_integration_compose import gen_integration_compose
from .test_constants import service_ports


this_dir = pathlib.Path(__file__).resolve().parent

ingestion_server = f"http://localhost:{service_ports['ingestion_server']}"


#################
# Bottle server #
#################


bottle_port = 58000
bottle_path = "/task_done"

if platform.system() == "Linux":
    host_address = "172.17.0.1"
else:
    host_address = "host.docker.internal"
bottle_url = f"http://{host_address}:{bottle_port}{bottle_path}"


def start_bottle(queue):
    bottle = Bottle()

    @bottle.route(bottle_path, method="post")
    def handle_task_callback():
        queue.put("CALLBACK!")
        return {"message": "OK"}

    bottle.run(host="0.0.0.0", port=bottle_port, quiet=False)


#####################
# Integration tests #
#####################


class TestIngestion(unittest.TestCase):
    compose_path = None

    @classmethod
    def _wait_for_dbs(cls):
        """
        Wait for databases to come up and establish connections to both.
        :return: the connections to the upstream and downstream databases
        """

        upstream_db = None
        downstream_db = None

        retries = 3
        while retries > 0:
            try:
                db_args = {
                    "connect_timeout": 5,
                    "dbname": "openledger",
                    "user": "deploy",
                    "password": "deploy",
                    "host": "localhost",
                }
                upstream_db = psycopg2.connect(
                    **db_args | {"port": service_ports["upstream_db"]}
                )
                downstream_db = psycopg2.connect(
                    **db_args | {"port": service_ports["db"]}
                )
                break
            except psycopg2.OperationalError as e:
                logging.debug(e)
                logging.info("Waiting for databases to be ready...")
                time.sleep(5)
                retries -= 1
                continue

        if upstream_db is not None and downstream_db is not None:
            logging.info("Connected to databases")
            return upstream_db, downstream_db
        else:
            raise ValueError("Could not connect to databases")

    @classmethod
    def _wait(cls, cmd):
        """
        Run the given long running command in a subprocess and block while that
        command executes.
        :param cmd: the long-running command to execute in a subprocess
        """

        subprocess.run(
            cmd,
            cwd=cls.compose_path.parent,
            check=True,
            capture_output=True,
        )

    @classmethod
    def _wait_for_es(cls) -> None:
        """
        Wait for Elasticsearch to come up.
        """

        logging.info("Waiting for ES to be ready...")
        port = service_ports["es"]
        cls._wait(["just", "wait-for-es", f"localhost:{port}"])
        logging.info("Connected to ES")

    @classmethod
    def _wait_for_ing(cls) -> None:
        """
        Wait for ingestion-server to come up.
        """

        logging.info("Waiting for ingestion-server to be ready...")
        port = service_ports["ingestion_server"]
        cls._wait(["just", "wait-for-ing", f"localhost:{port}"])
        logging.info("Connected to ingestion-server")

    @classmethod
    def _load_schemas(cls, conn, schema_names):
        cur = conn.cursor()
        for schema_name in schema_names:
            schema_path = this_dir.joinpath("mock_schemas", f"{schema_name}.sql")
            with open(schema_path, "r") as schema:
                cur.execute(schema.read())
        conn.commit()
        cur.close()

    @classmethod
    def _load_data(cls, conn, table_names):
        cur = conn.cursor()
        for table_name in table_names:
            data_path = this_dir.joinpath("mock_data", f"mocked_{table_name}.csv")
            with open(data_path, "r") as data:
                cur.copy_expert(
                    f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true)",
                    data,
                )
        conn.commit()
        cur.close()

    @classmethod
    def setUpClass(cls) -> None:
        # Launch a Bottle server to receive and handle callbacks
        cb_queue = Queue()
        cls.cb_queue = cb_queue
        cb_process = Process(target=start_bottle, args=(cb_queue,))
        cls.cb_process = cb_process
        cb_process.start()

        # Orchestrate containers with Docker Compose
        compose_path = gen_integration_compose()
        cls.compose_path = compose_path

        start_cmd = ["docker-compose", "-f", compose_path.name, "up", "-d"]
        subprocess.run(
            start_cmd,
            cwd=compose_path.parent,
            check=True,
            capture_output=True,
        )

        # Wait for services to be ready
        upstream_db, downstream_db = cls._wait_for_dbs()
        cls._wait_for_es()
        cls._wait_for_ing()

        # Set up the base scenario for the tests
        cls._load_schemas(upstream_db, ["audio_view", "audioset_view", "image_view"])
        cls._load_schemas(
            downstream_db,
            [
                "api_deletedaudio",
                "api_deletedimage",
                "api_matureaudio",
                "api_matureimage",
                "audio",
                "audioset",
                "image",
            ],
        )
        cls._load_data(upstream_db, ["audio_view", "image_view"])
        upstream_db.close()
        downstream_db.close()

    @classmethod
    def tearDownClass(cls) -> None:
        # Terminate the Bottle process started in ``setUp``
        cls.cb_process.terminate()

        # Stop all running containers and delete all data in volumes
        compose_path = cls.compose_path
        stop_cmd = ["docker-compose", "-f", compose_path.name, "down", "-v"]
        subprocess.run(
            stop_cmd,
            cwd=compose_path.parent,
            check=True,
            capture_output=True,
        )

    @pytest.mark.order(1)
    def test_list_tasks_empty(self):
        res = requests.get(f"{ingestion_server}/task")
        res_json = res.json()
        msg = "There should be no tasks in the task list"
        self.assertEqual(res_json, [], msg)

    @pytest.mark.order(2)
    def test_image_ingestion_succeeds(self):
        """
        Check that INGEST_UPSTREAM task completes successfully and responds
        with a callback.
        """
        req = {
            "model": "image",
            "action": "INGEST_UPSTREAM",
            "callback_url": bottle_url,
        }
        res = requests.post(f"{ingestion_server}/task", json=req)
        stat_msg = "The job should launch successfully and return 202 ACCEPTED."
        self.assertEqual(res.status_code, 202, msg=stat_msg)

        # Wait for the task to send us a callback.
        assert self.__class__.cb_queue.get(timeout=120) == "CALLBACK!"

    @pytest.mark.order(3)
    def test_task_count_after_one(self):
        res = requests.get(f"{ingestion_server}/task")
        res_json = res.json()
        msg = "There should be one task in the task list now."
        self.assertEqual(1, len(res_json), msg)

    @pytest.mark.order(4)
    def test_audio_ingestion_succeeds(self):
        """
        Check that INGEST_UPSTREAM task completes successfully and responds
        with a callback.
        """
        req = {
            "model": "audio",
            "action": "INGEST_UPSTREAM",
            "callback_url": bottle_url,
        }
        res = requests.post(f"{ingestion_server}/task", json=req)
        stat_msg = "The job should launch successfully and return 202 ACCEPTED."
        self.assertEqual(res.status_code, 202, msg=stat_msg)

        # Wait for the task to send us a callback.
        assert self.__class__.cb_queue.get(timeout=120) == "CALLBACK!"

    @pytest.mark.order(5)
    def test_task_count_after_two(self):
        res = requests.get(f"{ingestion_server}/task")
        res_json = res.json()
        msg = "There should be two tasks in the task list now."
        self.assertEqual(2, len(res_json), msg)

    def _get_es(self):
        return Elasticsearch(
            host="localhost",
            port=service_ports["es"],
            connection_class=RequestsHttpConnection,
            timeout=10,
            max_retries=10,
            retry_on_timeout=True,
            http_auth=None,
            wait_for_status="yellow",
        )

    @pytest.mark.order(6)
    def test_upstream_indexed_images(self):
        """
        Check that the image data has been successfully indexed in
        Elasticsearch. The number of hits for a blank search should match the
        size of the loaded mock data.
        """

        es = self._get_es()
        es_query = {"query": {"match_all": {}}}
        es.indices.refresh(index="image")
        search_response = es.search(index="image", body=es_query)
        msg = "There should be 5000 images in Elasticsearch after ingestion."
        self.assertEquals(search_response["hits"]["total"]["value"], 5000, msg)

    @pytest.mark.order(7)
    def test_upstream_indexed_audio(self):
        """
        Check that the audio data has been successfully indexed in
        Elasticsearch. The number of hits for a blank search should match the
        size of the loaded mock data.
        """

        es = self._get_es()
        es_query = {"query": {"match_all": {}}}
        es.indices.refresh(index="audio")
        search_response = es.search(index="audio", body=es_query)
        msg = "There should be 5000 audio tracks in Elasticsearch after ingestion."
        self.assertEquals(search_response["hits"]["total"]["value"], 5000, msg)
