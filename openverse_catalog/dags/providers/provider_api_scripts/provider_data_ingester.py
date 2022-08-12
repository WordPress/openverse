import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from airflow.models import Variable
from common.requester import DelayedRequester, RetriesExceeded
from common.storage.media import MediaStore
from common.storage.util import get_media_store_class
from requests.exceptions import JSONDecodeError, RequestException


logger = logging.getLogger(__name__)


class ProviderDataIngester(ABC):
    """
    An abstract base class that initializes media stores and ingests records
    from a given provider.

    Class variables of note:
    providers:   a dictionary whose keys are the supported `media_types`, and values are
                 the `provider` string in the `media` table of the DB for that type.
                 Used to initialize the media stores.
    endpoint:    the URL with which to request records from the API
    delay:       integer giving the minimum number of seconds to wait between
                 consecutive requests via the `get` method
    batch_limit: integer giving the number of records to get in each batch
    retries:     integer number of times to retry the request on error
    headers:     dictionary to be passed as headers to the request
    """

    delay = 1
    retries = 3
    batch_limit = 100
    headers: Dict = {}

    @property
    @abstractmethod
    def providers(self) -> dict[str, str]:
        """
        A dictionary whose keys are the supported `media_types`, and values are
        the `provider` string in the `media` table of the DB for that type.
        """
        pass

    @property
    @abstractmethod
    def endpoint(self):
        """
        The URL with which to request records from the API.
        """
        pass

    def __init__(self, date: str = None):
        """
        Optional Arguments:
        date: Date String in the form YYYY-MM-DD. This is the date for
              which running the script will pull data
        """
        # An airflow variable used to cap the amount of records to be ingested.
        # This can be used for testing purposes to ensure a provider script
        # processes some data but still returns quickly.
        # When set to 0, no limit is imposed.
        self.limit = Variable.get(
            "ingestion_limit", deserialize_json=True, default_var=0
        )

        # If a test limit is imposed, ensure that the `batch_limit` does not
        # exceed this.
        if self.limit:
            self.batch_limit = min(self.batch_limit, self.limit)

        # Initialize the DelayedRequester and all necessary Media Stores.
        self.delayed_requester = DelayedRequester(self.delay)
        self.media_stores = self.init_media_stores()
        self.date = date

    def init_media_stores(self) -> dict[str, MediaStore]:
        """
        Initialize a media store for each media type supported by this
        provider.
        """
        media_stores = {}

        for media_type, provider in self.providers.items():
            StoreClass = get_media_store_class(media_type)
            media_stores[media_type] = StoreClass(provider)

        return media_stores

    def ingest_records(self, **kwargs) -> None:
        """
        The main ingestion function that is called during the `pull_data` task.

        Optional Arguments:
        **kwargs: Optional arguments to be passed to `get_next_query_params`.
        """
        should_continue = True
        record_count = 0
        query_params = None

        logger.info(f"Begin ingestion for {self.__class__.__name__}")

        try:
            while should_continue:
                query_params = self.get_next_query_params(query_params, **kwargs)

                batch, should_continue = self.get_batch(query_params)

                if batch and len(batch) > 0:
                    record_count += self.process_batch(batch)
                    logger.info(f"{record_count} records ingested so far.")
                else:
                    logger.info("Batch complete.")
                    should_continue = False

                if self.limit and record_count >= self.limit:
                    logger.info(f"Ingestion limit of {self.limit} has been reached.")
                    should_continue = False
        finally:
            total = self.commit_records()
            logger.info(f"Committed {total} records")

    @abstractmethod
    def get_next_query_params(
        self, prev_query_params: Optional[Dict], **kwargs
    ) -> Dict:
        """
        Given the last set of query params, return the query params
        for the next request. Depending on the API, this may involve incrementing
        an `offset` or `page` param, for example.

        Required arguments:
        prev_query_params: Dictionary of query string params used in the previous
                           request. If None, this is the first request.
        **kwargs:          Optional kwargs passed through from `ingest_records`.

        """
        pass

    def get_batch(self, query_params: Dict) -> Tuple[Optional[List], bool]:
        """
        Given query params, request the next batch of records from the API and
        return them in a list.

        Required Arguments:
        query_params: query string parameters to be used in the request

        Return:
        batch:           list of records in the batch
        should_continue: boolean indicating whether ingestion should continue after
                         this batch has been processed
        """
        batch = None
        should_continue = True

        try:
            # Get the API response
            response_json = self.get_response_json(query_params)

            # Build a list of records from the response
            batch = self.get_batch_data(response_json)

            # Optionally, apply some logic to the response to determine whether
            # ingestion should continue or if should be short-circuited. By default
            # this will return True and ingestion continues.
            should_continue = self.get_should_continue(response_json)

        except (
            RequestException,
            RetriesExceeded,
            JSONDecodeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(f"Error getting next query parameters due to {e}")

        return batch, should_continue

    def get_response_json(self, query_params: Dict):
        """
        Make the actual API requests needed to ingest a batch. This can be overridden
        in order to support APIs that require multiple requests, for example.
        """
        return self.delayed_requester.get_response_json(
            self.endpoint, self.retries, query_params, headers=self.headers
        )

    def get_should_continue(self, response_json):
        """
        This method should be overridden when an API has additional logic for
        determining whether ingestion should continue. For example, this
        can be used to check for the existence of a `continue_token` in the
        response.
        """
        return True

    @abstractmethod
    def get_batch_data(self, response_json):
        """
        Take an API response and return the list of records.
        """
        pass

    def process_batch(self, media_batch):
        """
        Process a batch of records by adding them to the appropriate MediaStore.
        Returns the total count of records ingested up to this point, for all
        media types.
        """
        record_count = 0

        for data in media_batch:
            record_data = self.get_record_data(data)

            if record_data is None:
                continue

            record_data = (
                record_data
                if isinstance(record_data, list)
                else [
                    record_data,
                ]
            )

            for record in record_data:
                # We need to know what type of record we're handling in
                # order to add it to the correct store
                media_type = self.get_media_type(record)

                # Add the record to the correct store
                store = self.media_stores[media_type]
                store.add_item(**record)
                record_count += 1

        return record_count

    @abstractmethod
    def get_media_type(self, record: dict) -> str:
        """
        For a given record, return the media type it represents (eg "image", "audio",
        etc.) If a provider only supports a single media type, this may be hard-coded
        to return that type.
        """
        pass

    @abstractmethod
    def get_record_data(self, data: dict) -> dict | List[dict]:
        """
        Parse out the necessary information (license info, urls, etc) from the record
        data into a dictionary.

        If the record being parsed contains data for additional related records, a list
        may be returned of multiple record dictionaries.
        """
        pass

    def commit_records(self) -> int:
        total = 0
        for store in self.media_stores.values():
            total += store.commit()
        return total
