import time

import pytest
from elastic_transport import NodeConfig

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


def test_wait_uses_the_configured_timeout():
    assert _node(pool_timeout=1.5).pool.pool_timeout == 1.5


def test_https_is_rejected():
    with pytest.raises(ValueError, match="http scheme"):
        _node(scheme="https")
