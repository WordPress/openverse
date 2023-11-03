from __future__ import annotations

import functools
import logging as log
import pprint
import time

from django.conf import settings

from elasticsearch import BadRequestError, NotFoundError


def log_timing_info(func):
    @functools.wraps(func)
    def wrapper(*args, es_query, **kwargs):
        start_time = time.time()

        # Call the original function
        result = func(*args, **kwargs)

        response_time_in_ms = int((time.time() - start_time) * 1000)
        if hasattr(result, "took"):
            es_time_in_ms = result.took
        else:
            es_time_in_ms = result.get("took")
        log.info(
            {
                "response_time": response_time_in_ms,
                "es_time": es_time_in_ms,
                "es_query": es_query,
            }
        )

        return result

    return wrapper


@log_timing_info
def get_es_response(s, *args, **kwargs):
    if settings.VERBOSE_ES_RESPONSE:
        log.info(pprint.pprint(s.to_dict()))

    try:
        search_response = s.execute()

        if settings.VERBOSE_ES_RESPONSE:
            log.info(pprint.pprint(search_response.to_dict()))
    except (BadRequestError, NotFoundError) as e:
        raise ValueError(e)

    return search_response


@log_timing_info
def get_raw_es_response(index, body, *args, **kwargs):
    return settings.ES.search(index=index, body=body, *args, **kwargs)
