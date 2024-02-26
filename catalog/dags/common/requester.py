import logging
import time
from collections.abc import Callable

import requests
from airflow.exceptions import AirflowException
from requests.exceptions import JSONDecodeError

import oauth2
from common.loader import provider_details as prov


# pytest_socket will not be available in production, so we must create a shim for
# that specific exception so this code does not error out.
try:
    from pytest_socket import SocketConnectBlockedError
except ImportError:

    class SocketConnectBlockedError(Exception):
        pass


logger = logging.getLogger(__name__)


class RetriesExceeded(Exception):
    """Custom exception for when the number of allowed retries has been exceeded."""

    pass


class DelayedRequester:
    """
    Requester class with a built-in delay.

    Provides methods `get` and `head` that are wrappers around the `requests`
    module methods with the same name (i.e., it simply passes along whatever
    arguments it receives).  The difference is that when this class is initialized
    with a non-zero `delay` parameter, it waits for at least that number of seconds
    between consecutive requests. This is to avoid hitting rate limits of APIs.

    Optional Arguments:
    delay:   an integer giving the minimum number of seconds to wait
             between consecutive requests via the `get` method.
    headers: a dict that will be passed in all requests, unless overridden
             by kwargs in specific calls to the `get` method
    """

    def __init__(self, delay: int = 0, headers: dict | None = None):
        headers = {} if headers is None else headers
        self._DELAY = delay
        self.headers = {"User-Agent": prov.UA_STRING} | headers
        self._last_request = 0
        self.session = requests.Session()

    def _make_request(
        self, method: Callable[..., requests.models.Response], url: str, **kwargs
    ):
        """
        Make a request, and return the response object if it exists.

        Required Arguments:

        method:   `requests` module request method.
        url:      URL to make the request as a string.
        **kwargs: Optional arguments that will be passed to the `requests`
                  module request.
        """
        self._delay_processing()
        self._last_request = time.time()
        request_kwargs = kwargs or {}
        if "headers" not in kwargs:
            request_kwargs["headers"] = self.headers
        try:
            response = method(url, **request_kwargs)
            if response.status_code == requests.codes.ok:
                logger.debug(f"Received response from url {response.url}")
            elif response.status_code == requests.codes.unauthorized:
                logger.error(f"Authorization failed for URL: {response.url}")
            else:
                logger.warning(
                    f"Unable to request URL: {response.url}  "
                    f"Status code: {response.status_code}"
                )
            return response
        except SocketConnectBlockedError:
            # This exception will only be raised during testing, and it *must*
            # be re-raised and bubbled up the stack
            raise
        except (AirflowException, KeyboardInterrupt):
            # These exceptions are raised by task managers and should be respected &
            # re-raised. Airflow runs its tasks in a separate thread, so if this
            # exception is received, typically it means that the task has been
            # sent a SIGTERM, which means that the task should be stopped.
            raise
        except Exception as e:
            logger.error(f"Error with the request for URL: {url}")
            logger.info(f"{type(e).__name__}: {e}")
            if params := request_kwargs.get("params"):
                logger.info(f"Using query parameters {params}")
            logger.info(f'Using headers {request_kwargs.get("headers")}')
            return None

    def get(self, url, params=None, **kwargs):
        """
        Make a GET request, and return the response object if it exists.

        Required Arguments:

        url:      URL to make the request as a string.
        params:   Dictionary of query string params.
        **kwargs: Optional arguments that will be passed to `requests.get`.
        """
        return self._make_request(self.session.get, url, params=params, **kwargs)

    def head(self, url, **kwargs):
        """
        Make a HEAD request, and return the response object if it exists.

        Required Arguments:

        url:      URL to make the request as a string.
        **kwargs: Optional arguments that will be passed to `requests.head`.
        """
        return self._make_request(self.session.head, url, **kwargs)

    def post(self, url, params=None, **kwargs):
        """
        Make a POST request, and return the response object if it exists.

        Required Arguments:

        url:      URL to make the request as a string.
        params:   Dictionary of query string params.
        **kwargs: Optional arguments that will be passed to `requests.get`.
        """
        return self._make_request(self.session.post, url, params=params, **kwargs)

    def _delay_processing(self):
        wait = self._DELAY - (time.time() - self._last_request)
        if wait >= 0:
            logging.debug(f"Waiting {wait} second(s)")
            time.sleep(wait)

    def _get_json(self, response) -> dict | list | None:
        try:
            return response.json()
        except JSONDecodeError as e:
            logger.warning(f"Could not get response_json.\n{e}")

    def get_response_json(
        self, endpoint, retries=0, query_params=None, requestMethod="get", **kwargs
    ):
        response_json = None
        response = None
        if retries < 0:
            logger.error("No retries remaining.  Failure.")
            raise RetriesExceeded("Retries exceeded")

        if requestMethod == "get":
            response = self.get(endpoint, params=query_params, **kwargs)
        elif requestMethod == "post":
            response = self.post(endpoint, params=query_params, **kwargs)

        if response is not None and response.status_code == 200:
            response_json = self._get_json(response)

        if response_json is None or (
            isinstance(response_json, dict) and response_json.get("error") is not None
        ):
            logger.warning(f"Bad response_json:  {response_json}")
            logger.warning(
                "Retrying:\n_get_response_json(\n"
                f"    {endpoint},\n"
                f"    {query_params},\n"
                f"    retries={retries - 1}"
                ")"
            )
            response_json = self.get_response_json(
                endpoint, retries=retries - 1, query_params=query_params, **kwargs
            )

        return response_json


class OAuth2DelayedRequester(DelayedRequester):
    def __init__(self, provider_name: str, delay: int = 0):
        super().__init__(delay)
        # Replace session with Oauth one
        self.session = oauth2.get_oauth_client(provider_name)
