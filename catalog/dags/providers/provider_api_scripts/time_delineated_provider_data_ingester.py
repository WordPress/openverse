import logging
from abc import abstractmethod
from datetime import datetime, timedelta, timezone

from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class TimeDelineatedProviderDataIngester(ProviderDataIngester):
    """
    A subclass of ProviderDataIngester which breaks the ingestion interval into
    smaller intervals, and runs ingestion separately for each interval.

    Must be used on a dated DAG.

    Class variables of note:
    max_records:        integer giving the maximum number of records to be expected in
                        each interval
    division_threshold: integer threshold number of records in an hour, used to
                        determine how many divisions to use
    min_divisions:      integer giving the number of divisions to break an hour into if
                        the division_threshold is not exceeded
    max_divisions:      integer giving the number of divisions to break an hour into if
                        the division_threshold is exceeded
    should_raise_error: whether to raise an exception when more records are retrieved
                        from the API than the API reports to expect
    """

    min_divisions = 4  # 15-minute default intervals
    max_divisions = 12  # 5-minute default intervals
    should_raise_error = True

    @property
    @abstractmethod
    def max_records(self) -> int:
        pass

    @property
    @abstractmethod
    def division_threshold(self) -> int:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This class is used to generate timestamp intervals over a 24-hour period,
        # so it should only be used for a dated DAG.
        if self.date is None:
            raise ValueError(
                f"{self.__class__.__name__} should only be used for dated DAGs."
            )

        # A flag that is True only when we are processing the first batch of data in
        # a new iteration.
        self.new_iteration = True
        # Use to keep track of the number of records we've fetched from the API so far,
        # specifically in this iteration.
        self.fetched_count = 0

        # Keep track of our ts pairs
        self.timestamp_pairs = []

        # Keep track of the current ts pair
        self.current_timestamp_pair = ()

    @staticmethod
    def format_ts(timestamp):
        return timestamp.isoformat().replace("+00:00", "Z")

    @staticmethod
    def _get_timestamp_query_params_list(
        start_date: datetime, end_date: datetime, number_of_divisions: int
    ) -> list[tuple[datetime, datetime]]:
        """
        Given a start_date and end_date, returns a list of timestamp pairs that
        divides the time interval between them into equal portions, with the
        number of portions determined by `number_of_divisions`.

        Required Arguments:
        start_date:          datetime to be considered start of the interval
        end_date:            datetime to be considered end of the interval
        number_of_divisions: int number of portions to divide the interval into.
        """
        seconds_in_time_slice = (end_date - start_date).total_seconds()
        portion = int(seconds_in_time_slice / number_of_divisions)
        # Double check that the division resulted in even portions
        if seconds_in_time_slice % number_of_divisions:
            raise ValueError(
                f"The time slice from {start_date} to {end_date} cannot be divided "
                f"evenly into {number_of_divisions} parts!"
            )

        # Generate the start/end timestamps for each 'slice' of the interval
        return [
            (
                start_date + timedelta(seconds=i * portion),
                start_date + timedelta(seconds=(i + 1) * portion),
            )
            for i in range(number_of_divisions)
        ]

    @abstractmethod
    def get_record_count_from_response(self, response_json) -> int:
        # Given a response_json, return the response_count. This should not be the
        # number of records in the response, but the reported count.
        pass

    def _get_record_count(self, start: datetime, end: datetime, **kwargs) -> int:
        """Get the number of records returned by the API for a particular interval."""
        query_params = self.get_next_query_params(
            prev_query_params=None, start_ts=start, end_ts=end, **kwargs
        )
        response_json = self.get_response_json(query_params)

        return self.get_record_count_from_response(response_json)

    def _get_timestamp_pairs(self, **kwargs):
        """
        Determine a set of timestamp pairs.
        Some provider APIs can behave unexpectedly when querying large datasets,
        resulting in large numbers of duplicates and eventual DAG timeouts
        (see <https://github.com/WordPress/openverse-catalog/pull/879> for an
        example). To avoid this, when we detect that a time period contains a large
        number of records we split it up into multiple smaller time periods and
        run ingestion separately for each.

        Some runs of the DAG may have a very small (or zero) number of records, so in
        order to determine how many time intervals we need we first check the record
        count, and split into the smallest number of intervals possible.

        If the interval has no/few records, this results in ONE extra request.
        If the interval has a large amount of data, this results in TWENTY FIVE extra
        requests (one for the full day, and then one for each hour).
        """
        pairs_list: list[tuple[datetime, datetime]] = []
        # Get UTC timestamps for the start and end of the ingestion date
        start_ts = datetime.strptime(self.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_ts = start_ts + timedelta(days=1)

        record_count = self._get_record_count(start_ts, end_ts, **kwargs)
        if record_count == 0:
            logger.info("No data. Continuing.")
            return pairs_list
        if record_count < self.max_records:
            # This interval only has a small amount of data. We can ingest all of the
            # data for it in a single run.
            logger.info(
                f"Record count {record_count} is less than maximum of"
                f" {self.max_records}. Ingesting data for the full day at once."
            )
            return self._get_timestamp_query_params_list(start_ts, end_ts, 1)

        # If we got here, this day has a large amount of data. Since data is often
        # not distributed evenly across the day, we'll break down each hour of the day
        # separately. We add timestamp_pairs to the list only for hours that actually
        # contain data. Hours that contain more data get divided into a larger number of
        # portions.
        hour_slices = self._get_timestamp_query_params_list(start_ts, end_ts, 24)

        for start_hour, end_hour in hour_slices:
            # Get the number of records in this hour interval
            record_count = self._get_record_count(start_hour, end_hour, **kwargs)
            if record_count == 0:
                # No records for this hour, don't bother ingesting for this time period.
                logger.info(f"No data detected for {start_hour}. Continuing.")
                continue
            if record_count < self.max_records:
                # This hour doesn't have much data, ingest it in one chunk
                logger.info(
                    f"Record count {record_count} is less than maximum of"
                    f" {self.max_records}. Ingesting data for the full hour starting at"
                    f" {start_hour}."
                )
                pairs_list.append((start_hour, end_hour))
                continue
            # If we got this far, this hour has a lot of data. Check the count against
            # the division_threshold; if less than the threshold, we divide into the
            # smaller number of min_divisions. Otherwise, we use max_divisions
            num_divisions = (
                self.min_divisions
                if record_count < self.division_threshold
                else self.max_divisions
            )
            logger.info(
                f"Record count {record_count} is greater than maximum of"
                f" {self.max_records}. Ingesting data in {num_divisions} slices for the"
                f" hour starting at {start_hour}."
            )
            minute_slices = self._get_timestamp_query_params_list(
                start_hour, end_hour, num_divisions
            )
            pairs_list.extend(minute_slices)

        return pairs_list

    def get_fixed_query_params(self):
        self.timestamp_pairs = self._get_timestamp_pairs()
        if self.timestamp_pairs:
            logger.info(f"{len(self.timestamp_pairs)} timestamp pairs generated.")
        # Run ingestion for each timestamp pair. Override this method to
        # change the query param names if needed.
        return [
            {"start_ts": start_ts, "end_ts": end_ts}
            for start_ts, end_ts in self.timestamp_pairs
        ]

    def _ingest_records(
        self, initial_query_params: dict | None, fixed_query_params: dict | None
    ) -> None:
        """
        Override _ingest_records, which is called for each set of timestamp pairs,
        to reset the counts before each round.
        """
        # Update `current_timestamp_pair` to keep track of what we are processing.
        logger.info(fixed_query_params)
        self.current_timestamp_pair = (
            fixed_query_params["start_ts"],
            fixed_query_params["end_ts"],
        )

        # Reset counts
        self.new_iteration = True
        self.fetched_count = 0

        super()._ingest_records(initial_query_params, fixed_query_params)

    def get_should_continue(self, response_json) -> bool:
        """
        Update the `fetched_count` and `new_iteration` variables. Also adds
        some default error detection for a common bug where the ingester
        retrieves more records from the API than the reported total count.
        """

        # Get the total expected count for this time interval from the API.
        total_count = self.get_record_count_from_response(response_json)

        # Update the number of records we have pulled for this iteration.
        # Note that this tracks the number of records fetched from the API, not
        # the number "ingested", ie actually written to TSV (which may be larger
        # or smaller as some records are discarded or have additional related
        # images.)
        batch = self.get_batch_data(response_json)
        if batch:
            self.fetched_count += len(batch)

        if self.new_iteration:
            # This is the first batch of a new iteration.
            logger.info(f"Detected {total_count} total records.")
            self.new_iteration = False

        # Detect a bug when the API continues serving pages of data in excess of
        # the stated resultCount.
        if self.fetched_count > total_count:
            error_message = (
                f"Expected {total_count} records, but {self.fetched_count} have"
                " been fetched. Consider reducing the ingestion interval."
            )
            if self.should_raise_error:
                raise Exception(error_message)
            else:
                logger.info(error_message)

        # If `should_raise_error` was enabled, the error is raised and ingestion
        # halted. If not, we want to log but continue ingesting.
        return True
