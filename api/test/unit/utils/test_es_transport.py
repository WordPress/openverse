import time

import pytest
from elastic_transport import NodeConfig
from urllib3 import HTTPSConnectionPool

from api.utils.es_transport import BoundedWaitUrllib3HttpNode, SearchCapacityExceeded


def _node(pool_timeout=0.05, scheme="http"):
    node_class = BoundedWaitUrllib3HttpNode.with_pool_timeout(pool_timeout)
    return node_class(
        NodeConfig(scheme=scheme, host="127.0.0.1", port=9, connections_per_node=1)
    )


def test_request_gives_up_when_no_socket_frees_up_in_time():
    node = _node()
    node.pool._get_conn()  # the only socket is now busy

    start = time.monotonic()
    with pytest.raises(SearchCapacityExceeded):
        node.perform_request("GET", "/")
    assert time.monotonic() - start < 1


def test_timed_out_requests_do_not_add_slots_to_the_pool():
    node = _node()
    conn = node.pool._get_conn()

    for _ in range(3):
        with pytest.raises(SearchCapacityExceeded):
            node.perform_request("GET", "/")
    assert node.pool.pool.qsize() == 0

    node.pool._put_conn(conn)
    assert node.pool.pool.qsize() == 1


def test_wait_uses_the_configured_timeout():
    assert _node(pool_timeout=1.5).pool_timeout == 1.5


def test_https_pool_is_kept():
    assert isinstance(_node(scheme="https").pool, HTTPSConnectionPool)
