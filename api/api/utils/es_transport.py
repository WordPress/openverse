"""Elasticsearch transport node that refuses to wait for a socket forever."""

from __future__ import annotations

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


class BoundedWaitUrllib3HttpNode(Urllib3HttpNode):
    """
    ``Urllib3HttpNode`` whose socket pool gives up after ``pool_timeout``.

    Per-task request concurrency is otherwise unbounded (Django's ASGI handler
    runs each request on its own thread), so under a slow cluster the default
    node queued searches for minutes with ``request_timeout`` never engaging.
    """

    pool_timeout: float = 5.0

    def __init__(self, config: NodeConfig):
        super().__init__(config)
        # Wrap the pool the base class built rather than rebuilding it, so its
        # TLS configuration survives. ``urlopen`` already takes the wait
        # deadline as ``pool_timeout``; ``elastic_transport`` just never passes
        # one. The translation must happen outside ``urlopen`` because its
        # cleanup treats ``EmptyPoolError`` specially: raising anything else
        # from the acquisition makes it "release" a connection it never got,
        # which adds a phantom slot to the pool.
        urlopen = self.pool.urlopen

        def urlopen_with_deadline(*args, **kwargs):
            kwargs.setdefault("pool_timeout", self.pool_timeout)
            try:
                return urlopen(*args, **kwargs)
            except EmptyPoolError as e:
                raise SearchCapacityExceeded(
                    f"No Elasticsearch connection free within {self.pool_timeout} s"
                ) from e

        self.pool.urlopen = urlopen_with_deadline

    @classmethod
    def with_pool_timeout(cls, seconds: float) -> type[BoundedWaitUrllib3HttpNode]:
        """Return a subclass for ``Elasticsearch(node_class=...)``, which takes no instance."""
        return type(cls.__name__, (cls,), {"pool_timeout": seconds})
