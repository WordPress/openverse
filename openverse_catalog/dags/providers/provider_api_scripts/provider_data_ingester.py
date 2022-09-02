import json
import logging
import traceback
from abc import ABC, abstractmethod

from airflow.exceptions import AirflowException
from airflow.models import Variable
from common.requester import DelayedRequester, RetriesExceeded
from common.storage.media import MediaStore
from common.storage.util import get_media_store_class
from requests.exceptions import JSONDecodeError, RequestException


logger = logging.getLogger(__name__)


class AggregateIngestionError(Exception):
    """
    Custom exception when multiple ingestion errors are skipped and then
    raised in aggregate at the end of ingestion.
    """

    pass


class IngestionError(Exception):
    """
    Custom exception which includes information about the query_params that
    were being used when the error was encountered.
    """

    def __init__(self, error, traceback, query_params):
        self.error = error
        self.traceback = traceback
        self.query_params = json.dumps(query_params)

    def __str__(self):
        # Append query_param info to error message
        return f"{self.error}\nquery_params: {self.query_params}"

    def repr_with_traceback(self):
        # Append traceback
        return f"{str(self)}\n{self.traceback}"


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
    headers: dict = {}

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

    def __init__(self, conf: dict = None, date: str = None):
        """
        Optional Arguments:
        conf: The configuration dict for the running DagRun
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

        # dag_run configuration options
        conf = conf or {}

        # Used to skip over errors and continue ingestion. When enabled, errors
        # are not reported until ingestion has completed.
        self.skip_ingestion_errors = conf.get("skip_ingestion_errors", False)
        self.ingestion_errors: list[IngestionError] = []  # Keep track of errors

        # An optional set of initial query params from which to begin ingestion.
        self.initial_query_params = conf.get("initial_query_params")

        # An optional list of `query_params`. When provided, ingestion will be run for
        # just these sets of params.
        self.override_query_params = None
        if query_params_list := conf.get("query_params_list"):
            # Create a generator to facilitate fetching the next set of query_params.
            self.override_query_params = (qp for qp in query_params_list)

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

        while should_continue:
            query_params = self.get_query_params(query_params, **kwargs)
            if query_params is None:
                # Break out of ingestion if no query_params are supplied. This can
                # happen when the final `override_query_params` is processed.
                break

            try:
                batch, should_continue = self.get_batch(query_params)

                if batch and len(batch) > 0:
                    record_count += self.process_batch(batch)
                    logger.info(f"{record_count} records ingested so far.")
                else:
                    logger.info("Batch complete.")
                    should_continue = False

            except AirflowException as error:
                # AirflowExceptions should not be caught, as execution should not
                # continue when the task is being stopped by Airflow.

                # If errors have already been caught during processing, raise them
                # as well.
                if error_summary := self.get_ingestion_errors():
                    raise error_summary from error
                raise

            except Exception as error:
                ingestion_error = IngestionError(
                    error, traceback.format_exc(), query_params
                )

                if self.skip_ingestion_errors:
                    # Add this to the errors list but continue processing
                    self.ingestion_errors.append(ingestion_error)
                    logger.error(f"Skipping batch due to ingestion error: {error}")
                    continue

                # Commit whatever records we were able to process, and rethrow the
                # exception so the taskrun fails.
                self.commit_records()
                raise error from ingestion_error

            if self.limit and record_count >= self.limit:
                logger.info(f"Ingestion limit of {self.limit} has been reached.")
                should_continue = False

        # Commit whatever records we were able to process
        self.commit_records()

        # If errors were caught during processing, raise them now
        if error_summary := self.get_ingestion_errors():
            raise error_summary

    def get_ingestion_errors(self) -> AggregateIngestionError | None:
        """
        If any errors were skipped during ingestion, log them as well as the
        associated query parameters. Then return an AggregateIngestionError.

        It there are no errors to report, returns None.
        """
        if self.ingestion_errors:
            # Log the affected query_params
            bad_query_params = ", \n".join(
                [f"{e.query_params}" for e in self.ingestion_errors]
            )
            logger.info(
                "The following query_params resulted in errors: \n"
                f"{bad_query_params}"
            )
            errors_str = "\n".join(
                e.repr_with_traceback() for e in self.ingestion_errors
            )
            logger.error(
                f"The following errors were encountered during ingestion:\n{errors_str}"
            )
            return AggregateIngestionError(
                f"{len(self.ingestion_errors)} query batches were skipped due to "
                "errors during ingestion using the `skip_ingestion_errors` flag. "
                "See the log for more details."
            )
        return None

    def get_query_params(self, prev_query_params: dict | None, **kwargs) -> dict | None:
        """
        Returns the next set of query_params for the next request, handling
        optional overrides via the dag_run conf.
        """
        # If we are getting query_params for the first batch and initial_query_params
        # have been set, return them.
        if prev_query_params is None and self.initial_query_params:
            logger.info(
                "Using initial_query_params from dag_run conf:"
                f" {json.dumps(self.initial_query_params)}"
            )
            return self.initial_query_params

        # If a list of query_params was provided, return the next value.
        if self.override_query_params:
            next_params = next(self.override_query_params, None)
            logger.info(
                "Using query params from `query_params_list` set in dag_run conf:"
                f" {next_params}"
            )
            return next_params

        # Default behavior when no conf options are provided; build the next
        # set of query params, given the previous.
        return self.get_next_query_params(prev_query_params, **kwargs)

    @abstractmethod
    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        """
        Given the last set of query params, return the query params
        for the next request. Depending on the API, this may involve incrementing
        an `offset` or `page` param, for example.

        Required arguments:
        prev_query_params: dictionary of query string params used in the previous
                           request. If None, this is the first request.
        **kwargs:          Optional kwargs passed through from `ingest_records`.

        """
        pass

    def get_batch(self, query_params: dict) -> tuple[list | None, bool]:
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

        # Get the API response
        try:
            response_json = self.get_response_json(query_params)
        except (
            RequestException,
            RetriesExceeded,
            JSONDecodeError,
            ValueError,
            TypeError,
        ) as e:
            logger.error(f"Error getting response due to {e}")
            response_json = None

        # Build a list of records from the response
        batch = self.get_batch_data(response_json)

        # Optionally, apply some logic to the response to determine whether
        # ingestion should continue or if should be short-circuited. By default
        # this will return True and ingestion continues.
        should_continue = self.get_should_continue(response_json)

        return batch, should_continue

    def get_response_json(self, query_params: dict, endpoint: str | None = None):
        """
        Make the actual API requests needed to ingest a batch. This can be overridden
        in order to support APIs that require multiple requests, for example.
        """
        return self.delayed_requester.get_response_json(
            endpoint or self.endpoint,
            self.retries,
            query_params,
            headers=self.headers,
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
    def get_record_data(self, data: dict) -> dict | list[dict] | None:
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
        logger.info(f"Committed {total} records")
        return total
