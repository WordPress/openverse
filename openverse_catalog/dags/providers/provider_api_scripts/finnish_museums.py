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
BUILDINGS = ["0/Suomen kansallismuseo/", "0/Museovirasto/", "0/SATMUSEO/", "0/SA-kuva/"]


class FinnishMuseumsDataIngester(ProviderDataIngester):
    providers = {"image": PROVIDER}
    endpoint = "https://api.finna.fi/api/v1/search"
    batch_limit = 100
    delay = 5
    format_type = "0/Image/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # A flag that is turned on each time we start ingestion for a new set of
        # query params. This is useful for logging information on only the first
        # batch of each set.
        self.new_iteration = True

        # Build the list of timestamp pairs once, so they can be reused for each
        # building queried.
        self.timestamp_pairs = self._get_timestamp_query_params_list(self.date)

    @staticmethod
    def _get_timestamp_query_params_list(date):
        """
        The Finnish Museums API behaves unexpectedly when querying large datasets,
        resulting in large numbers of duplicates and eventual DAG timeouts
        (see https://github.com/WordPress/openverse-catalog/pull/879 for more
        details). To avoid this, we build a list of timestamp pairs that divide
        the ingestion date into equal portions of the 24-hour period, and run
        ingestion separately for each time slice.
        """
        # Get the logical date for the DagRun
        utc_date = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

        seconds_in_a_day = 86400
        number_of_divisions = 48  # Half-hour increments
        portion = int(seconds_in_a_day / number_of_divisions)

        def _format_timestamp(d):
            return d.isoformat().replace("+00:00", "Z")

        # Generate the start/end timestamps for each half-hour 'slice' of the day
        pair_list = [
            (
                _format_timestamp(utc_date + timedelta(seconds=i * portion)),
                _format_timestamp(utc_date + timedelta(seconds=(i + 1) * portion)),
            )
            for i in range(number_of_divisions)
        ]
        return pair_list

    def ingest_records(self, **kwargs):
        for building in BUILDINGS:
            logger.info(f"Obtaining images of building {building}")

            for start_ts, end_ts in self.timestamp_pairs:
                self.new_iteration = True

                logger.info(f"Ingesting data for start: {start_ts}, end: {end_ts}")
                super().ingest_records(
                    building=building, start_ts=start_ts, end_ts=end_ts
                )

    def get_next_query_params(self, prev_query_params, **kwargs):
        if not prev_query_params:
            building = kwargs.get("building")
            start_ts = kwargs.get("start_ts")
            end_ts = kwargs.get("end_ts")

            return {
                "filter[]": [
                    f'format:"{self.format_type}"',
                    f'building:"{building}"',
                    f'last_indexed:"[{start_ts} TO {end_ts}]"',
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

        if self.new_iteration:
            logger.info(f"Detected {response_json['resultCount']} total records.")
            self.new_iteration = False

        return response_json["records"]

    def get_record_data(self, data):
        records = []

        license_url = self.get_license_url(data)
        if license_url is None:
            return None

        foreign_identifier = data.get("id")
        if foreign_identifier is None:
            return None
        title = data.get("title")
        building = data.get("buildings")[0].get("value")
        source = next(
            (s for s in SUB_PROVIDERS if building in SUB_PROVIDERS[s]), PROVIDER
        )
        foreign_landing_url = LANDING_URL + foreign_identifier

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


def main():
    ingester = FinnishMuseumsDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
