"""
Content Provider:       Finnish Museums

ETL Process:            Use the API to identify all CC licensed images.

Output:                 TSV file containing the images and the
                        respective meta-data.

Notes:                  https://api.finna.fi/swagger-ui/
                        https://www.finna.fi/Content/help-syntax?lng=en-gb
                        The Finnish Museums provider script is a dated DAG that
                        ingests all records that were last updated in the previous
                        day. Because of this, it is not necessary to run a separate
                        reingestion DAG, as updated data will be processed during
                        regular ingestion.
"""
import logging
from datetime import datetime, timedelta, timezone
from itertools import chain

from airflow.exceptions import AirflowException
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s:  %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

API_URL = "https://api.finna.fi"
LANDING_URL = "https://www.finna.fi/Record/"

PROVIDER = prov.FINNISH_DEFAULT_PROVIDER
SUB_PROVIDERS = prov.FINNISH_SUB_PROVIDERS


class FinnishMuseumsDataIngester(ProviderDataIngester):
    providers = {"image": PROVIDER}
    endpoint = "https://api.finna.fi/api/v1/search"
    batch_limit = 100
    delay = 5
    format_type = "0/Image/"
    buildings = [
        "0/Suomen kansallismuseo/",
        "0/Museovirasto/",
        "0/SATMUSEO/",
        "0/SA-kuva/",
    ]

    def __init__(self, *args, **kwargs):
        """
        Note: this DAG runs ingestion separately for each configured `building`. When a
        building has many records for the ingestion date, the DAG further splits up
        ingestion into time slices. Each run of the `ingest_records` function for
        a particular (building, time slice) pair is an "iteration" of the DAG.

        For logging and alerting purposes, we maintain several instance variables
        that help track each iteration.
        """
        # A flag that is True only when we are processing the first batch of data in
        # a new iteration.
        self.new_iteration = True
        # Use to keep track of the number of records we've fetched from the API so far,
        # specifically in this iteration.
        self.fetched_count = 0

        super().__init__(*args, **kwargs)

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

    def _get_record_count(self, start: datetime, end: datetime, building: str) -> int:
        """
        Get the number of records returned by the Finnish Museums API for a
        particular building, during a given time interval.
        """
        query_params = self.get_next_query_params(
            prev_query_params=None, building=building, start_ts=start, end_ts=end
        )
        response_json = self.get_response_json(query_params)

        if response_json:
            return response_json.get("resultCount", 0)
        return 0

    def _get_timestamp_pairs(self, building: str):
        """
        Determine a set of timestamp pairs per building.
        The Finnish Museums API can behave unexpectedly when querying large datasets,
        resulting in large numbers of duplicates and eventual DAG timeouts
        (see https://github.com/WordPress/openverse-catalog/pull/879 for more
        details). To avoid this, when we detect that a time period contains a large
        number of records we split it up into multiple smaller time periods and
        run ingestion separately for each.

        Most runs of the DAG will have a very small (or zero) number of records, so in
        order to determine how many time intervals we need we first check the record
        count, and split into the smallest number of intervals possible.

        If the building has no/few records, this results in ONE extra request.
        If the building has a large amount of data, this results in TWENTY FIVE extra
        requests (one for the full day, and then one for each hour).
        """
        pairs_list: list[tuple[datetime, datetime]] = []
        # Get UTC timestamps for the start and end of the ingestion date
        start_ts = datetime.strptime(self.date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_ts = start_ts + timedelta(days=1)

        record_count = self._get_record_count(start_ts, end_ts, building)
        if record_count == 0:
            logger.info(f"No data for {building}. Continuing.")
            return pairs_list
        if record_count < 10_000:
            # This building only has a small amount of data. We can ingest all of the
            # data for it in a single run.
            return self._get_timestamp_query_params_list(start_ts, end_ts, 1)

        # If we got here, this building has a large amount of data. Since data is often
        # not distributed evenly across the day, we'll break down each hour of the day
        # separately. We add timestamp_pairs to the list only for hours that actually
        # contain data. Hours that contain more data get divided into a larger number of
        # portions.
        hour_slices = self._get_timestamp_query_params_list(start_ts, end_ts, 24)
        for (start_hour, end_hour) in hour_slices:
            # Get the number of records in this hour interval
            record_count = self._get_record_count(start_hour, end_hour, building)
            if record_count == 0:
                # No records for this hour, don't bother ingesting for this time period.
                logger.info(f"No data detected for {start_hour}. Continuing.")
                continue
            if record_count < 10_000:
                # This hour doesn't have much data, ingest it in one chunk
                pairs_list.append((start_hour, end_hour))
                continue
            # If we got this far, this hour has a lot of data. It is split into 12 5-min
            # intervals if it has fewer than 100k, or 20 3-min intervals if more.
            num_divisions = 12 if record_count < 100_000 else 20
            minute_slices = self._get_timestamp_query_params_list(
                start_hour, end_hour, num_divisions
            )
            pairs_list.extend(minute_slices)

        return pairs_list

    def ingest_records(self, **kwargs):
        for building in self.buildings:
            logger.info(f"Obtaining images of building {building}")

            # Get the timestamp pairs. If there are no records for this building,
            # it will be an empty list.
            timestamp_pairs = self._get_timestamp_pairs(building)

            # Run ingestion for each timestamp pair
            for start_ts, end_ts in timestamp_pairs:
                # Reset counts before we start
                self.new_iteration = True
                self.fetched_count = 0

                logger.info(f"Ingesting data for start: {start_ts}, end: {end_ts}")
                super().ingest_records(
                    building=building, start_ts=start_ts, end_ts=end_ts
                )

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            building = kwargs.get("building")
            start_ts = self.format_ts(kwargs.get("start_ts"))
            end_ts = self.format_ts(kwargs.get("end_ts"))

            return {
                "filter[]": [
                    f'format:"{self.format_type}"',
                    f'building:"{building}"',
                    f'last_indexed:"[{start_ts} TO {end_ts}]"',
                ],
                "field[]": [
                    "authors",
                    "buildings",
                    "id",
                    "imageRights",
                    "images",
                    "subjects",
                    "title",
                ],
                "limit": self.batch_limit,
                "page": 1,
            }
        return {**prev_query_params, "page": prev_query_params["page"] + 1}

    def get_media_type(self, record):
        return "image"

    def get_batch_data(self, response_json):
        if (
            response_json is None
            or str(response_json.get("status")).lower() != "ok"
            or response_json.get("records") is None
            or len(response_json.get("records")) == 0
        ):
            return None

        total_count = response_json.get("resultCount")
        # Update the number of records we have pulled for this iteration.
        # Note that this tracks the number of records pulled from the API, not
        # the number actually written to TSV (which may be larger or smaller
        # as some records are discarded or have additional related images.)
        self.fetched_count += len(response_json.get("records"))

        if self.new_iteration:
            # This is the first batch of a new iteration.
            logger.info(f"Detected {total_count} total records.")
            self.new_iteration = False

        # Detect a bug when the API continues serving pages of data in excess of
        # the stated resultCount.
        if self.fetched_count > total_count:
            raise AirflowException(
                f"Expected {total_count} records, but {self.fetched_count} have"
                " been fetched. Consider reducing the ingestion interval."
            )

        return response_json["records"]

    def get_record_data(self, data):
        records = []

        license_url = self.get_license_url(data)
        if license_url is None:
            return None

        foreign_identifier = data.get("id")
        if foreign_identifier is None:
            return None
        foreign_landing_url = LANDING_URL + foreign_identifier

        title = data.get("title")
        creator = self.get_creator(data.get("authors")) if data.get("authors") else None
        building = data.get("buildings")[0].get("value")
        source = next(
            (s for s in SUB_PROVIDERS if building in SUB_PROVIDERS[s]), PROVIDER
        )

        raw_tags = None
        tag_lists = data.get("subjects")
        if tag_lists is not None:
            raw_tags = list(chain(*tag_lists))

        image_list = data.get("images")
        for img in image_list:
            image_url = self._get_image_url(img)
            records.append(
                {
                    "license_info": get_license_info(license_url),
                    "foreign_identifier": foreign_identifier,
                    "foreign_landing_url": foreign_landing_url,
                    "image_url": image_url,
                    "title": title,
                    "source": source,
                    "creator": creator,
                    "raw_tags": raw_tags,
                }
            )
        return records

    @staticmethod
    def get_license_url(obj):
        license_url = obj.get("imageRights", {}).get("link")
        if license_url is None:
            return None

        # The API returns urls linking to the Finnish version of the license deed,
        # (eg `licenses/by/4.0/deed.fi`), but the license validation logic expects
        # links to the license page (eg `license/by/4.0`).
        return license_url.removesuffix("deed.fi")

    @staticmethod
    def _get_image_url(img, image_url=API_URL):
        if img is None:
            return None
        return image_url + img

    @staticmethod
    def get_creator(authors_raw):
        authors = []
        for author_type in ["primary", "secondary", "corporate"]:
            author = authors_raw.get(author_type)
            if author is None or type(author) != dict:
                continue
            author = "; ".join(list(author.keys()))
            authors.append(author)

        return "; ".join(authors) or None


def main():
    ingester = FinnishMuseumsDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
