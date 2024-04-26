import json
import logging
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TypedDict

from airflow.exceptions import AirflowException
from airflow.models import Variable

from common.loader import provider_details as prov
from common.requester import DelayedRequester
from common.storage.media import MediaStore
from common.storage.util import get_media_store_class


logger = logging.getLogger(__name__)


class AggregateIngestionError(Exception):
    """
    Combined error for all ingestion errors.

    Custom exception when multiple ingestion errors are skipped and then
    raised in aggregate at the end of ingestion.
    """

    pass


class IngestionError(Exception):
    """
    Ingestion error which occurred during processing.

    Custom exception which includes information about the query_params that
    were being used when the error was encountered.
    """

    def __init__(self, error, traceback, query_params):
        self.error = error
        self.traceback = traceback
        self.query_params = json.dumps(query_params, default=str)

    def __str__(self):
        # Append query_param info to error message
        return f"{self.error}\nquery_params: {self.query_params}"

    def repr_with_traceback(self):
        # Append traceback
        return f"{str(self)}\n{self.traceback}"


class SkippedIngestionError(TypedDict):
    """
    Configuration for a silenced ingestion error.

    issue:     A link to a GitHub issue which describes why the error
               is silenced and tracks resolving the problem.
    predicate: Errors whose classname or message contain the predicate will be
               skipped. Matching is case-insensitive.
    """

    issue: str
    predicate: str


class ProviderDataIngester(ABC):
    """
    ABC which initializes media stores and ingests records from a given provider.

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
        Providers supported by this ingester.

        A dictionary mapping each supported media type to its corresponding
        `provider` string (the string that will populate the `provider` field
        in the Catalog DB). These strings should be defined as constants in
        common.loader.provider_details.py

        By convention, when a provider supports multiple media types we set
        separate provider strings for each type. For example:

        ```
        providers = {
            "image": provider_details.MYPROVIDER_IMAGE_PROVIDER,
            "audio": provider_details.MYPROVIDER_AUDIO_PROVIDER,
        }
        ```
        """
        pass

    @property
    @abstractmethod
    def endpoint(self):
        """The URL with which to request records from the API."""
        pass

    def __init__(
        self,
        conf: dict = None,
        dag_id: str = None,
        date: str = None,
        day_shift: int = None,
    ):
        """
        Initialize the provider configuration.
        Optional Arguments:

        conf: The configuration dict for the running DagRun
        dag_id: The id of the running provider DAG
        date: Date String in the form YYYY-MM-DD. This is the date for
              which running the script will pull data
        """
        # An airflow variable used to cap the amount of records to be ingested.
        # This can be used for testing purposes to ensure a provider script
        # processes some data but still returns quickly.
        # When set to 0, no limit is imposed.
        self.limit = Variable.get(
            "INGESTION_LIMIT", deserialize_json=True, default_var=0
        )

        # If a test limit is imposed, ensure that the `batch_limit` does not
        # exceed this.
        if self.limit:
            self.batch_limit = min(self.batch_limit, self.limit)

        # Keep track of number of records ingested
        self.record_count = 0

        # Set default headers
        self.headers = {"User-Agent": prov.UA_STRING} | self.headers

        # Initialize the DelayedRequester and all necessary Media Stores.
        self.delayed_requester = DelayedRequester(
            delay=self.delay, headers=self.headers
        )
        self.media_stores = self._init_media_stores(day_shift)
        self.date = date
        self.dag_id = dag_id or ""

        # dag_run configuration options
        conf = conf or {}

        # Allow overriding the date with a %Y-%m-%d string from the dagrun conf.
        date_override = conf.get("date")
        if date_override and datetime.strptime(date_override, "%Y-%m-%d"):
            self.date = date_override
        if self.date:
            logger.info(f"Using date {self.date}.")

        # An optional set of initial query params from which to begin ingestion.
        self.initial_query_params = conf.get("initial_query_params")

        # An optional list of `query_params`. When provided, ingestion will be run for
        # just these sets of params.
        self.override_query_params = None
        if query_params_list := conf.get("query_params_list"):
            # Create a generator to facilitate fetching the next set of query_params.
            self.override_query_params = (qp for qp in query_params_list)

        # An optional set of query params to add to all queries
        self.additional_query_params = conf.get("additional_query_params", {})

        # A configuration option that is used to skip over ALL errors and continue
        # ingestion, reporting errors in aggregate when ingestion has completed. This
        # option should be used sparingly and can only be enabled at the level of an
        # individual DagRun.
        self.skip_all_ingestion_errors = conf.get("skip_ingestion_errors", False)

        # Global configuration for particular errors that should be skipped across all
        # runs of this DAG. Only errors matching the configuration will be skipped, and
        # reported in aggregate when ingestion has completed.
        self.skipped_ingestion_errors: list[SkippedIngestionError] = Variable.get(
            "SKIPPED_INGESTION_ERRORS", default_var={}, deserialize_json=True
        ).get(self.dag_id, [])

        self.ingestion_errors: list[IngestionError] = []  # Keep track of skipped errors

    def _init_media_stores(self, day_shift: int = None) -> dict[str, MediaStore]:
        """Initialize a media store for each media type supported by this provider."""

        media_stores = {}
        tsv_suffix = str(day_shift) if day_shift else None

        for media_type, provider in self.providers.items():
            StoreClass = get_media_store_class(media_type)
            media_stores[media_type] = StoreClass(provider, tsv_suffix=tsv_suffix)

        return media_stores

    def _ingest_records(
        self, initial_query_params: dict | None, fixed_query_params: dict | None
    ) -> None:
        """
        Perform ingestion.

        Required Arguments:

        Optional Arguments:
        initial_query_params:    Optional override for the query params to be used in the
                                 first batch.
        fixed_query_params:      Optional, fixed query params which should be passed to
                                 `get_next_query_params`. These should not change during this
                                 round of ingestion.
        """
        should_continue = True
        # Use initial_query_params if provided, or get the next set of params.
        query_params = initial_query_params or self._get_query_params(
            None, fixed_query_params
        )
        if initial_query_params:
            logger.info(
                "Using initial_query_params from dag_run conf:"
                f" {json.dumps(self.initial_query_params)}"
            )

        # If an ingestion limit has been set and we have already ingested records
        # in excess of the limit, exit early. This may happen if `ingest_records`
        # is called more than once.
        if self.limit and self.record_count >= self.limit:
            return

        logger.info(f"Begin ingestion for {self.__class__.__name__}")

        while should_continue:
            if query_params is None:
                # Break out of ingestion if no query_params are supplied. This can
                # happen when the final `override_query_params` is processed.
                break

            try:
                batch, should_continue = self.get_batch(query_params)

                if batch and len(batch) > 0:
                    self.record_count += self.process_batch(batch)
                    logger.info(f"{self.record_count} records ingested so far.")
                else:
                    logger.info("Batch complete.")
                    should_continue = False

            except AirflowException as error:
                # AirflowExceptions should not be caught or reraised as IngestionErrors,
                # as execution should not continue when the task is being stopped by
                # Airflow. However, we should still log the last query_params to be
                # hit before the error was raised.
                logger.info(
                    f"Last query_params used: {json.dumps(query_params, default=str)}"
                )

                # If errors have already been caught during processing, raise them
                # as well.
                if error_summary := self._get_ingestion_errors():
                    raise error_summary from error
                raise

            except Exception as error:
                ingestion_error = IngestionError(
                    error, traceback.format_exc(), query_params
                )

                if self._should_skip_ingestion_error(error):
                    # Add this to the errors list but continue processing
                    self.ingestion_errors.append(ingestion_error)
                    logger.error(f"Skipping batch due to ingestion error: {error}")

                    # Continue from the next batch
                    query_params = self._get_query_params(
                        query_params, fixed_query_params
                    )
                    continue

                # Commit whatever records we were able to process, and rethrow the
                # exception so the taskrun fails.
                self._commit_records()
                raise error from ingestion_error

            if self.limit and self.record_count >= self.limit:
                logger.info(f"Ingestion limit of {self.limit} has been reached.")
                should_continue = False

            # Get next query params
            query_params = self._get_query_params(query_params, fixed_query_params)

        # Commit whatever records we were able to process
        self._commit_records()

        # If errors were caught during processing, raise them now
        if error_summary := self._get_ingestion_errors():
            raise error_summary

    def ingest_records(self) -> None:
        """
        Ingest all records.

        If fixed_query_params are provided, ingestion will be performed separately
        for each set of fixed_query_params.

        This is the main ingestion function that is called during the `pull_data` task.
        """
        # If no fixed params were provided, simply begin ingestion
        if not (fixed_query_params := self.get_fixed_query_params()):
            return self._ingest_records(self.initial_query_params, {})

        # Else, ingestion should be run separately for each set of fixed_query_params.

        # If initial_query_params were also provided, we should being ingestion
        # from the first set of fixed_query_params that is included in the
        # initial_query_params
        if self.initial_query_params:
            initial_fixed_params = next(
                (
                    qp
                    for qp in fixed_query_params
                    if qp.items() <= self.initial_query_params.items()
                ),
                fixed_query_params[0],
            )

            logger.info(
                "First fixed query parameter matching the initial_query_params"
                f" was: {initial_fixed_params}."
            )

            # Run ingestion on the first batch, passing in the initial_query_params
            self._ingest_records(self.initial_query_params, initial_fixed_params)

            # Resume from the _next_ set of fixed_query_params
            fixed_query_params = fixed_query_params[
                fixed_query_params.index(initial_fixed_params) + 1 :
            ]

        logger.info(
            "Ingestion will be performed for each of the following sets of"
            f" fixed query parameters: {fixed_query_params}"
        )

        for fixed_params in fixed_query_params:
            logger.info(f"==Starting ingestion with fixed params: {fixed_params}==")
            # Subsequent batches should not start at the initial_query_params
            self._ingest_records(None, fixed_params)

    def _should_skip_ingestion_error(self, error: Exception) -> bool:
        """Determine whether an error should be skipped."""
        if self.skip_all_ingestion_errors:
            return True

        for skipped_error in self.skipped_ingestion_errors:
            # Check if the predicate matches
            if skipped_error["predicate"].lower() in repr(error).lower():
                return True

        return False

    def _get_ingestion_errors(self) -> AggregateIngestionError | None:
        """
        Retrieve all ingestion errors that have been caught during processing.

        If any errors were skipped during ingestion, log them as well as the
        associated query parameters. Then return an AggregateIngestionError.

        If there are no errors to report, returns None.
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

    def _get_query_params(
        self, prev_query_params: dict | None, fixed_query_params: dict | None = None
    ) -> dict | None:
        """
        Return the next set of query_params for the next request.

        This handles optional overrides via the dag_run conf.
        This method should not be overridden; instead override get_next_query_params.
        """
        # If a list of query_params was provided, return the next value.
        if self.override_query_params:
            next_params = next(self.override_query_params, None)
            logger.info(
                "Using query params from `query_params_list` set in dag_run conf:"
                f" {next_params}"
            )
            return next_params

        # Default behavior: build the next set of query params, given the previous.
        # The final set of query params returned merges:
        # * the `next_query_params` calculated based on the previous params
        # * any `fixed_query_params`, which are fixed params that do not change
        #   depending on the previous params, and are applied to all batches in this
        #   round of ingestion
        # * any `additional_query_params`, which are provided via the DagRun conf
        #   and applied to all batches, in every round of ingestion
        next_query_params = self.get_next_query_params(prev_query_params)
        fixed_query_params = fixed_query_params or {}
        return next_query_params | fixed_query_params | self.additional_query_params

    def get_fixed_query_params(self) -> list[dict] | None:
        """
        Return a list of fixed query params, for each of which ingestion will be
        performed.
        """
        return []

    @abstractmethod
    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        """
        Get the next set of query parameters.

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
        Get a batch of records from the API.

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
        response_json = self.get_response_json(query_params)

        # Build a list of records from the response
        batch = self.get_batch_data(response_json)

        # Optionally, apply some logic to the response to determine whether
        # ingestion should continue or if should be short-circuited. By default
        # this will return True and ingestion continues.
        should_continue = self.get_should_continue(response_json)

        return batch, should_continue

    def get_response_json(
        self, query_params: dict, endpoint: str | None = None, **kwargs
    ):
        """
        Make the actual API requests needed to ingest a batch.

        This can be overridden in order to support APIs that require multiple requests,
        for example.
        """
        return self.delayed_requester.get_response_json(
            endpoint or self.endpoint,
            self.retries,
            query_params,
            headers=self.headers,
            **kwargs,
        )

    def get_should_continue(self, response_json):
        """
        Determine whether ingestion should continue after this batch has been processed.

        This method should be overridden when an API has additional logic for
        determining whether ingestion should continue. For example, this
        can be used to check for the existence of a `continue_token` in the
        response.
        """
        return True

    @abstractmethod
    def get_batch_data(self, response_json) -> None | list[dict]:
        """Take an API response and return the list of records."""
        pass

    def process_batch(self, media_batch) -> int:
        """
        Process a batch of records by adding them to the appropriate MediaStore.

        Returns the total count of records ingested up to this point, for all
        media types.
        """
        processed_count = 0

        for data in media_batch:
            if not (record_data := self.get_record_data(data)):
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
                processed_count += 1

                if self.limit and (self.record_count + processed_count) >= self.limit:
                    logger.info("Ingestion limit has been reached. Halting processing.")
                    return processed_count

        return processed_count

    def get_media_type(self, record: dict) -> str:
        """
        Return the media type a record represents.

        (eg "image", "audio", etc.)
        If a provider only supports a single media type, this method defaults
        to returning the only media type defined in the ``providers`` attribute.
        """
        if len(self.providers) == 1:
            return list(self.providers.keys())[0]

        raise NotImplementedError(
            "Provider scripts that support multiple media types "
            "must provide an override for ``get_media_type``."
        )

    @abstractmethod
    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        """
        Parse out the necessary information from the record data into a dictionary.

        Examples include license info, urls, etc. If the record being parsed contains
        data for additional related records, a list may be returned of multiple
        record dictionaries.
        """
        pass

    def _commit_records(self) -> int:
        total = 0
        for store in self.media_stores.values():
            total += store.commit()
        logger.info(f"Committed {total} records")
        return total
