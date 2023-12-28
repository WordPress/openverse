import logging as log
import time
from typing import NamedTuple

from decouple import config
from elasticsearch import ConnectionError as EsConnectionError
from elasticsearch import Elasticsearch, NotFoundError


class Stat(NamedTuple):
    """Contains information about the index or alias identified by its name."""

    exists: bool
    is_alias: bool | None
    alt_names: str | list[str] | None


def elasticsearch_connect(timeout: int = 300) -> Elasticsearch:
    """
    Repeatedly try to connect to Elasticsearch until successful.

    :param timeout: the amount of time in seconds to wait for a successful connection
    :return: an Elasticsearch client.
    """

    while timeout > 0:
        try:
            return _elasticsearch_connect()
        except EsConnectionError as err:
            log.exception(err)
            log.error("Reconnecting to Elasticsearch in 5 seconds...")
            timeout -= 5
            time.sleep(5)
            continue


def _elasticsearch_connect() -> Elasticsearch:
    """
    Connect to an Elasticsearch indices at the configured domain.

    This method also handles AWS authentication using the AWS access key ID and the
    secret access key.

    :return: an Elasticsearch client
    """

    es_scheme = config("ELASTICSEARCH_SCHEME", default="http://")
    es_url = config("ELASTICSEARCH_URL", default="localhost")
    es_port = config("ELASTICSEARCH_PORT", default=9200, cast=int)

    es_endpoint = f"{es_scheme}{es_url}:{es_port}"

    timeout = 12  # hours

    es = Elasticsearch(
        es_endpoint,
        timeout=timeout * 3600,  # seconds
    )
    es.info()
    return es


def get_stat(es: Elasticsearch, name_or_alias: str) -> Stat:
    """
    Get more information about the index name or alias given to the function.

    For any given input, the function offers three bits of information:

    - whether an alias or index of the name exists
    - whether the name is an alias
    - the index name that the alias points to/the aliases associated with the index

    :param es: the Elasticsearch connection
    :param name_or_alias: the name of the index or an alias associated with it
    :return: a ``Stat`` instance containing the three bits of information
    """

    try:
        matches = es.indices.get(index=name_or_alias)
        real_name = list(matches.keys())[0]
        aliases = list(matches[real_name]["aliases"].keys())
        is_alias = real_name != name_or_alias
        return Stat(
            exists=True,
            is_alias=is_alias,
            alt_names=real_name if is_alias else aliases,
        )
    except NotFoundError:
        return Stat(exists=False, is_alias=None, alt_names=None)
