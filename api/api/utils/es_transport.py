"""Elasticsearch transport node that refuses to wait for a socket forever."""

from __future__ import annotations

import urllib3
from elastic_transport import NodeConfig, Urllib3HttpNode
from urllib3.exceptions import EmptyPoolError


class SearchCapacityExceeded(RuntimeError):
    """
    No pooled Elasticsearch socket became free within the configured wait.

    This deliberately subclasses ``RuntimeError``: ``elastic_transport``
    re-raises builtin exceptions untouched, whereas anything else raised by a
    node is wrapped in ``ConnectionError``, retried and used to mark the node
    dead. None of that is wanted when the node is fine and we are the ones
    saturating it.
    """


class _BoundedWaitPool(urllib3.HTTPConnectionPool):
    def __init__(self, *args, pool_timeout: float, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool_timeout = pool_timeout

    def _get_conn(self, timeout: float | None = None):
        # ``urlopen`` only passes a wait deadline when its caller supplies
        # ``pool_timeout``, which ``elastic_transport`` never does, so a
        # blocking pool waits indefinitely unless the default is set here.
        try:
            return super()._get_conn(
                timeout=self.pool_timeout if timeout is None else timeout
            )
        except EmptyPoolError as e:
            raise SearchCapacityExceeded(
                f"No Elasticsearch connection free within {self.pool_timeout} s"
            ) from e


class BoundedWaitUrllib3HttpNode(Urllib3HttpNode):
    """
    ``Urllib3HttpNode`` whose socket pool gives up after ``pool_timeout``.

    Per-task request concurrency is otherwise unbounded (Django's ASGI handler
    runs each request on its own thread), so under a slow cluster the default
    node queued searches for minutes with ``request_timeout`` never engaging.
    Only plain HTTP is supported; the TLS set-up in the base class is not
    replicated here.
    """

    pool_timeout: float = 5.0

    def __init__(self, config: NodeConfig):
        if config.scheme != "http":
            raise ValueError(
                f"{type(self).__name__} only supports the http scheme, "
                f"got {config.scheme!r}"
            )
        super().__init__(config)
        self.pool.close()
        self.pool = _BoundedWaitPool(
            config.host,
            port=config.port,
            timeout=urllib3.Timeout(total=config.request_timeout),
            maxsize=config.connections_per_node,
            block=True,
            pool_timeout=self.pool_timeout,
        )

    @classmethod
    def with_pool_timeout(cls, seconds: float) -> type[BoundedWaitUrllib3HttpNode]:
        """Return a subclass for ``Elasticsearch(node_class=...)``, which takes no instance."""
        return type(cls.__name__, (cls,), {"pool_timeout": seconds})
