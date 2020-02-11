import logging
import requests
import time

logger = logging.getLogger(__name__)


class DelayedRequester:
    """
    Provides a method `get` that is a wrapper around `get` from the
    `requests` module (i.e., it simply passes along whatever arguments it
    receives).  The difference is that when this class is initialized
    with a non-zero `delay` parameter, it waits for at least that number
    of seconds between consecutive requests. This is to avoid hitting
    rate limits of APIs.

    Optional Arguments:
    delay:  an integer giving the minimum number of seconds to wait
            between consecutive requests via the `get` method.
    """
    def __init__(self, delay=0):
        self._DELAY = delay
        self._last_request = 0

    def get(self, url, params=None, **kwargs):
        """
        Make a get request, and return the response json if it exists.

        Required Arguments:

        url:      URL to make the request as a string.
        params:   Dictionary of query string params
        **kwargs: Optional arguments that will be passed to `requests.get`
         """
        logger.info(f'Processing request for url: {url}')
        logger.info(f'Using query parameters {params}')
        logger.info(f'Using headers {kwargs.get("headers")}')
        self._delay_processing()
        self._last_request = time.time()
        try:
            response = requests.get(url, params=params, **kwargs)
            if response.status_code == requests.codes.ok:
                return response
            else:
                logger.warning(
                    f'Unable to request URL: {url}.  '
                    f'Status code: {response.status_code}'
                )
                return response
        except Exception as e:
            logger.error('There was an error with the request.')
            logger.info(f'{type(e).__name__}: {e}')
            return None

    def _delay_processing(self):
        wait = self._DELAY - (time.time() - self._last_request)
        if wait >= 0:
            logging.debug(f'Waiting {wait} second(s)')
            time.sleep(wait)
