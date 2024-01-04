"""
Integration test for the ingestion-server.

This test spins up Docker containers, loads media items into the upstream database, and
ensures that the data has been copied and indexed downstream.
"""

import logging
import pathlib
import platform
import subprocess
import time
from multiprocessing import Process, Queue

import psycopg2
import pytest
import requests

# Uses Bottle because, unlike Falcon, it can be run from within the test suite.
from bottle import Bottle
from elasticsearch import Elasticsearch, NotFoundError

from .gen_integration_compose import gen_integration_compose
from .test_constants import service_ports


this_dir = pathlib.Path(__file__).resolve().parent

ingestion_server = f"http://localhost:{service_ports['ingestion_server']}"

mock_sensitive_terms = (
    (this_dir.parent / "ingestion_server" / "static" / "mock_sensitive_terms.txt")
    .read_text()
    .split("\n")
)

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


compose_path = None


def _wait_for_dbs():
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
            downstream_db = psycopg2.connect(**db_args | {"port": service_ports["db"]})
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


def _wait(compose_path, cmd):
    """
    Run the given long-running command in a subprocess and block while it runs.

    :param cmd: the long-running command to execute in a subprocess
    """

    subprocess.run(
        cmd,
        cwd=compose_path.parent,
        check=True,
        capture_output=True,
    )


def _wait_for_es(compose_path) -> None:
    """Wait for Elasticsearch to come up."""

    logging.info("Waiting for ES to be ready...")
    port = service_ports["es"]
    # Point to the root `justfile` to avoid automatic resolution to the nearest.
    _wait(compose_path, ["just", "../../docker/es/wait", f"localhost:{port}"])
    logging.info("Connected to ES")


def _wait_for_ing(compose_path) -> None:
    """Wait for ingestion-server to come up."""

    logging.info("Waiting for ingestion-server to be ready...")
    port = service_ports["ingestion_server"]
    # Automatically resolves to the nearest `justfile`.
    _wait(compose_path, ["just", "wait", f"localhost:{port}"])
    logging.info("Connected to ingestion-server")


def _load_schemas(conn, schema_names):
    cur = conn.cursor()
    for schema_name in schema_names:
        schema_path = this_dir.joinpath("mock_schemas", f"{schema_name}.sql")
        with open(schema_path) as schema:
            cur.execute(schema.read())
    conn.commit()
    cur.close()


def _load_data(conn, table_names):
    cur = conn.cursor()
    for table_name in table_names:
        data_path = this_dir.joinpath("../../sample_data", f"sample_{table_name}.csv")
        with open(data_path) as data:
            cur.copy_expert(
                f"COPY {table_name} FROM STDIN WITH (FORMAT csv, HEADER true)",
                data,
            )
    conn.commit()
    cur.close()


def _compose_cmd(compose_path, cmd: list[str], **kwargs):
    """Run a Docker Compose command"""

    cmd = [
        "docker-compose",
        "--profile",
        "ingestion_server",
        "-f",
        compose_path,
        *cmd,
    ]
    subprocess.run(
        cmd,
        cwd=compose_path.parent,
        check=True,
        **kwargs,
    )


def _get_constraints(conn, table) -> dict[str, str]:
    """Get the constraints on a given table using a given connection."""

    constraint_sql = f"""
            SELECT conname, pg_get_constraintdef(c.oid)
            FROM pg_constraint AS c
            JOIN pg_namespace AS n
            ON n.oid = c.connamespace
            AND n.nspname = 'public'
            AND conrelid::regclass::text = '{table}'
            ORDER BY conrelid::regclass::text, contype DESC;
    """
    with conn.cursor() as cursor:
        cursor.execute(constraint_sql)
        return {constraint: name for name, constraint in cursor}


def _get_index_parts(index: str, table: str) -> list[str]:
    """
    Strip out common keywords from the index to get a the name & columns.

    Indices take the form of:
        CREATE [UNIQUE] INDEX {name} ON {table} USING btree {columns}
    Output will look like: ["my_special_index", "(my_column)"]
    """
    for token in [
        "CREATE",
        "UNIQUE",
        "INDEX",
        "ON",
        "USING",
        f"public.{table}",
        "btree",
    ]:
        index = index.replace(f"{token} ", "")
    return index.split(" ", maxsplit=1)


def _get_indices(conn, table) -> dict[str, str]:
    """Get the indices on a given table using a given connection."""

    index_sql = f"SELECT indexdef FROM pg_indexes WHERE tablename = '{table}';"
    with conn.cursor() as cursor:
        cursor.execute(index_sql)
        indices = [_get_index_parts(row[0], table) for row in cursor]
        idx_mapping = {columns: name for name, columns in indices}
        return idx_mapping


def _ingest_upstream(cb_queue, downstream_db, model, suffix="integration"):
    """Check that INGEST_UPSTREAM task succeeds and responds with a callback."""

    before_indices = _get_indices(downstream_db, model)
    before_constraints = _get_constraints(downstream_db, model)
    req = {
        "model": model,
        "action": "INGEST_UPSTREAM",
        "index_suffix": suffix,
        "callback_url": bottle_url,
    }
    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    logging.info(f"Waiting for the task to send us a callback {cb_queue}")

    # Wait for the task to send us a callback.
    assert cb_queue.get(timeout=240) == "CALLBACK!"

    # Check that the indices remained the same
    after_indices = _get_indices(downstream_db, model)
    after_constraints = _get_constraints(downstream_db, model)
    assert (
        before_indices == after_indices
    ), "Indices in DB don't match the names they had before the go-live"
    assert (
        before_constraints == after_constraints
    ), "Constraints in DB don't match the names they had before the go-live"


@pytest.fixture()
def sample_es():
    endpoint = f"http://localhost:{service_ports['es']}"
    es = Elasticsearch(
        endpoint,
        request_timeout=10,
        max_retries=10,
        retry_on_timeout=True,
    )
    es.cluster.health(wait_for_status="yellow")
    return es


def _promote(sample_es, cb_queue, model, suffix="integration", alias=None):
    """Check that PROMOTE task succeeds and configures alias mapping in ES."""

    if alias is None:
        alias = model
    req = {
        "model": model,
        "action": "PROMOTE",
        "index_suffix": suffix,
        "alias": alias,
        "callback_url": bottle_url,
    }
    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    # Wait for the task to send us a callback.
    cb_queue.get(timeout=120) == "CALLBACK!"

    es = sample_es
    assert list(es.indices.get(index=alias).keys())[0] == f"{model}-{suffix}"


def check_index_exists(index_name, sample_es):
    es = sample_es
    assert es.indices.get(index=index_name) is not None


def _point_alias(sample_es, cb_queue, model, suffix, alias):
    req = {
        "model": model,
        "action": "POINT_ALIAS",
        "index_suffix": suffix,
        "alias": alias,
        "callback_url": bottle_url,
    }

    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    assert cb_queue.get(timeout=30) == "CALLBACK!"

    check_index_exists(alias, sample_es)


def _delete_index(sample_es, cb_queue, model, suffix="integration", alias=None):
    req = {
        "model": model,
        "action": "DELETE_INDEX",
        "callback_url": bottle_url,
    }
    if alias is None:
        req |= {"index_suffix": suffix}
    else:
        req |= {
            "alias": alias,
            "force_delete": True,
        }
    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    # Wait for the task to send us a callback.
    assert cb_queue.get(timeout=120) == "CALLBACK!"

    es = sample_es
    with pytest.raises(NotFoundError):
        es.indices.get(index=f"{model}-{suffix}")


def _soft_delete_index(
    sample_es, model, alias, suffix="integration", omit_force_delete=False
):
    """
    Send a soft delete request.

    Deleting without the ``force_delete`` flag set to ``True`` is
    considered a soft-delete because it will be declined if the target is
    an alias. Not providing the flag is equivalent to setting it to
    ``False``.
    """

    req = {
        "model": model,
        "action": "DELETE_INDEX",
        "alias": alias,
    }
    if not omit_force_delete:
        req |= {"force_delete": False}
    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should fail fast and return 400 BAD REQUEST."
    assert res.status_code == 400, stat_msg
    check_index_exists(f"{model}-{suffix}", sample_es)


def _create_and_populate_filtered_index(
    sample_es,
    cb_queue,
    model,
    origin_suffix=None,
    destination_suffix=None,
):
    req = {
        "model": model,
        "action": "CREATE_AND_POPULATE_FILTERED_INDEX",
        "callback_url": bottle_url,
    }
    if origin_suffix is not None:
        req |= {
            "origin_index_suffix": origin_suffix,
        }
    if destination_suffix is not None:
        req |= {"destination_index_suffix": destination_suffix}

    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    assert cb_queue.get(timeout=60) == "CALLBACK!"

    index_pattern = (
        f"{model}-{destination_suffix if destination_suffix else '*'}-filtered"
    )
    check_index_exists(index_pattern, sample_es)


@pytest.fixture(scope="module", autouse=True)
def setup_fixture():
    # Launch a Bottle server to receive and handle callbacks
    cb_queue = Queue()
    cb_process = Process(target=start_bottle, args=(cb_queue,))
    cb_process.start()

    # Orchestrate containers with Docker Compose
    compose_path = gen_integration_compose()

    _compose_cmd(compose_path, ["up", "-d"])

    # Wait for services to be ready
    upstream_db, downstream_db = _wait_for_dbs()
    _wait_for_es(compose_path)
    _wait_for_ing(compose_path)

    # Set up the base scenario for the tests
    _load_schemas(
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
    _load_data(upstream_db, ["audio", "image"])
    setup = {}
    setup["cb_queue"] = cb_queue
    setup["cb_process"] = cb_process
    setup["compose_path"] = compose_path
    setup["upstream_db"] = upstream_db
    setup["downstream_db"] = downstream_db
    yield setup

    # Teardown: Clean up resources (if any) after the test
    cb_process.terminate()

    # Close connections with databases
    for conn in [upstream_db, downstream_db]:
        if conn:
            conn.close()


def test_list_tasks_empty():
    res = requests.get(f"{ingestion_server}/task")
    res_json = res.json()
    msg = "There should be no tasks in the task list"
    assert res_json == [], msg


@pytest.mark.order(after="test_list_tasks_empty")
def test_image_ingestion_succeeds(setup_fixture):
    _ingest_upstream(
        setup_fixture["cb_queue"],
        setup_fixture["downstream_db"],
        "image",
        "integration",
    )


@pytest.mark.order(after="test_image_ingestion_succeeds")
def test_task_count_after_one():
    res = requests.get(f"{ingestion_server}/task")
    res_json = res.json()
    msg = "There should be one task in the task list now."
    assert 1 == len(res_json), msg


@pytest.mark.order(after="test_task_count_after_one")
def test_audio_ingestion_succeeds(setup_fixture):
    _ingest_upstream(
        setup_fixture["cb_queue"],
        setup_fixture["downstream_db"],
        "audio",
        "integration",
    )


@pytest.mark.order(after="test_audio_ingestion_succeeds")
def test_task_count_after_two():
    res = requests.get(f"{ingestion_server}/task")
    res_json = res.json()
    msg = "There should be two tasks in the task list now."
    assert 2 == len(res_json), msg


@pytest.mark.order(after="test_task_count_after_two")
def test_promote_images(sample_es, setup_fixture):
    _promote(sample_es, setup_fixture["cb_queue"], "image", "integration", "image-main")


@pytest.mark.order(after="test_promote_images")
def test_promote_audio(sample_es, setup_fixture):
    _promote(sample_es, setup_fixture["cb_queue"], "audio", "integration", "audio-main")


@pytest.mark.order(after="test_promote_audio")
def test_upstream_indexed_images(sample_es):
    """
    Check that the image data has been successfully indexed in Elasticsearch.

    The number of hits for a blank search should match the size of the loaded mock
    data.
    """

    es = sample_es
    es.indices.refresh(index="image-integration")
    count = es.count(index="image-integration")["count"]
    msg = "There should be 5000 images in Elasticsearch after ingestion."
    assert count == 5000, msg


@pytest.mark.order(after="test_upstream_indexed_images")
def test_upstream_indexed_audio(sample_es):
    """
    Check that the audio data has been successfully indexed in Elasticsearch.

    The number of hits for a blank search should match the size of the loaded mock
    data.
    """

    es = sample_es
    es.indices.refresh(index="audio-integration")
    count = es.count(index="audio-integration")["count"]
    msg = "There should be 5000 audio tracks in Elasticsearch after ingestion."
    assert count == 5000, msg


@pytest.mark.order(after="test_promote_images")
def test_filtered_image_index_creation(setup_fixture, sample_es):
    _create_and_populate_filtered_index(
        sample_es, setup_fixture["cb_queue"], "image", "integration", "integration"
    )


@pytest.mark.order(after="test_promote_audio")
def test_filtered_audio_index_creation(setup_fixture, sample_es):
    _create_and_populate_filtered_index(
        sample_es, setup_fixture["cb_queue"], "audio", "integration", "integration"
    )


@pytest.mark.order(after="test_filtered_image_index_creation")
def test_point_filtered_image_alias(setup_fixture, sample_es):
    _point_alias(
        sample_es,
        setup_fixture["cb_queue"],
        "image",
        "integration-filtered",
        "image-filtered",
    )


@pytest.mark.order(after="test_filtered_audio_index_creation")
def test_point_filtered_audio_alias(setup_fixture, sample_es):
    _point_alias(
        sample_es,
        setup_fixture["cb_queue"],
        "audio",
        "integration-filtered",
        "audio-filtered",
    )


@pytest.mark.order(
    after=["test_point_filtered_audio_alias", "test_point_filtered_image_alias"]
)
@pytest.mark.parametrize(
    "sensitive_term, index",
    zip(mock_sensitive_terms, ["audio-filtered", "image-filtered"]),
)
def test_filtered_indexes(sample_es, sensitive_term, index):
    """
    Check that the sensitive terms are correctly filtered out.

    Each sensitive term should have zero exact matches for it when querying
    the filtered index. We use `term` against the `.raw` fields to ensure this.
    """
    es = sample_es
    queryable_fields = ["title", "description", "tags.name"]
    query = {
        "bool": {
            "should": [
                {"term": {f"{field}.raw": sensitive_term}} for field in queryable_fields
            ]
        }
    }
    res = es.search(index=index, query=query)
    count = res["hits"]["total"]["value"]
    assert (
        count == 0
    ), f"There should be no results that exactly match {sensitive_term} in {index}. Found {count}."


@pytest.mark.order(after="test_upstream_indexed_audio")
def test_update_index_images(setup_fixture):
    """Check that the image data can be updated from the API database into ES."""

    req = {
        "model": "image",
        "action": "UPDATE_INDEX",
        "since_date": "1999-01-01",
        "index_suffix": "integration",
        "callback_url": bottle_url,
    }
    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    # Wait for the task to send us a callback.
    assert setup_fixture["cb_queue"].get(timeout=120) == "CALLBACK!"


@pytest.mark.order(after="test_update_index_images")
def test_update_index_audio(setup_fixture):
    """Check that the audio data can be updated from the API database into ES."""

    req = {
        "model": "audio",
        "action": "UPDATE_INDEX",
        "since_date": "1999-01-01",
        "index_suffix": "integration",
        "callback_url": bottle_url,
    }
    res = requests.post(f"{ingestion_server}/task", json=req)
    stat_msg = "The job should launch successfully and return 202 ACCEPTED."
    assert res.status_code == 202, stat_msg

    # Wait for the task to send us a callback.
    assert setup_fixture["cb_queue"].get(timeout=120) == "CALLBACK!"


@pytest.mark.order(after="test_update_index_audio")
def test_index_deletion_succeeds(setup_fixture, sample_es):
    _ingest_upstream(
        setup_fixture["cb_queue"], setup_fixture["downstream_db"], "audio", "temporary"
    )
    _delete_index(sample_es, setup_fixture["cb_queue"], "audio", "temporary")


@pytest.mark.order(after="test_index_deletion_succeeds")
def test_alias_force_deletion_succeeds(setup_fixture, sample_es):
    _ingest_upstream(
        setup_fixture["cb_queue"], setup_fixture["downstream_db"], "audio", "temporary"
    )
    _promote(sample_es, setup_fixture["cb_queue"], "audio", "temporary", "audio-temp")
    _delete_index(
        sample_es, setup_fixture["cb_queue"], "audio", "temporary", "audio-temp"
    )


@pytest.mark.order(after="test_alias_force_deletion_succeeds")
def test_alias_soft_deletion_fails(setup_fixture, sample_es):
    _ingest_upstream(
        setup_fixture["cb_queue"], setup_fixture["downstream_db"], "audio", "temporary"
    )
    _promote(sample_es, setup_fixture["cb_queue"], "audio", "temporary", "audio-temp")
    _soft_delete_index(sample_es, "audio", "audio-temp", "temporary")


@pytest.mark.order(after="test_alias_soft_deletion_fails")
def test_alias_ambiguous_deletion_fails(setup_fixture, sample_es):
    # No need to ingest or promote, index and alias exist
    _soft_delete_index(sample_es, "audio", "audio-temp", "temporary", True)


@pytest.mark.order(after="test_alias_ambiguous_deletion_fails")
def test_stat_endpoint_for_index():
    res = requests.get(f"{ingestion_server}/stat/audio-integration")
    data = res.json()
    assert data["exists"]
    assert data["alt_names"] == ["audio-main"]


@pytest.mark.order(after="test_stat_endpoint_for_index")
def test_stat_endpoint_for_alias():
    res = requests.get(f"{ingestion_server}/stat/audio-main")
    data = res.json()
    assert data["exists"]
    assert data["alt_names"] == "audio-integration"


@pytest.mark.order(after="test_stat_endpoint_for_alias")
def test_stat_endpoint_for_non_existent():
    res = requests.get(f"{ingestion_server}/stat/non-existent")
    data = res.json()
    assert not data["exists"]
