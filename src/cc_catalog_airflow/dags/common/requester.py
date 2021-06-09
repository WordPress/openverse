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
        Make a get request, and return the response object if it exists.

        Required Arguments:

        url:      URL to make the request as a string.
        params:   Dictionary of query string params
        **kwargs: Optional arguments that will be passed to `requests.get`
         """
        self._delay_processing()
        self._last_request = time.time()
        try:
            response = requests.get(url, params=params, **kwargs)
            if response.status_code == requests.codes.ok:
                logger.info(f'Received response from url {response.url}')
                return response
            else:
                logger.warning(
                    f'Unable to request URL: {response.url}.  '
                    f'Status code: {response.status_code}'
                )
                return response
        except Exception as e:
            logger.error(f'Error with the request for url: {url}.')
            logger.info(f'{type(e).__name__}: {e}')
            logger.info(f'Using query parameters {params}')
            logger.info(f'Using headers {kwargs.get("headers")}')
            return None

    def _delay_processing(self):
        wait = self._DELAY - (time.time() - self._last_request)
        if wait >= 0:
            logging.debug(f'Waiting {wait} second(s)')
            time.sleep(wait)

    def get_response_json(
            self,
            endpoint,
            retries=0,
            query_params=None,
            **kwargs
    ):
        response_json = None

        if retries < 0:
            logger.error('No retries remaining.  Failure.')
            raise Exception('Retries exceeded')

        response = self.get(endpoint, params=query_params, **kwargs)
        if response is not None and response.status_code == 200:
            try:
                response_json = response.json()
            except Exception as e:
                logger.warning(f'Could not get response_json.\n{e}')
                response_json = None

        if (
                response_json is None or response_json.get('error') is not None
        ):
            logger.warning(f'Bad response_json:  {response_json}')
            logger.warning(
                'Retrying:\n_get_response_json(\n'
                f'    {endpoint},\n'
                f'    {query_params},\n'
                f'    retries={retries - 1}'
                ')'
            )
            response_json = self.get_response_json(
                endpoint,
                retries=retries - 1,
                query_params=query_params,
                **kwargs
            )

        return response_json
