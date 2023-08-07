"""
TODO: This doc string will be used to generate documentation for the DAG in
DAGs.md. Update it to include any relevant information that you'd like to
be documented.

Content Provider:       XenoCanto

ETL Process:            Use the API to identify all CC licensed media.

Output:                 TSV file containing the media and the
                        respective meta-data.

Notes:                  https://xeno-canto.org/explore/api
"""
import logging
from datetime import datetime, timedelta

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class XenoCantoDataIngester(ProviderDataIngester):
    """
    This is a template for a ProviderDataIngester.

    Methods are shown with example implementations. Adjust them to suit your API.
    """

    providers = {
        "audio": prov.XENO_CANTO_AUDIO_PROVIDER,
    }
    endpoint = "https://xeno-canto.org/api/2/recordings"
    delay = 1
    retries = 3

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_pages = None
        self.current_page = 1

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        # On the first request, `prev_query_params` will be `None`. We can detect this
        # and return our default params.
        if not prev_query_params:
            run_date = datetime.fromisoformat(self.date)
            params = {
                "year": run_date.year,
                "month": run_date.month,
            }
        else:
            # On subsequent requests, increment the page by one and return the params
            self.current_page += 1
            params = prev_query_params

        return {**params, "page": self.current_page}

    def get_should_continue(self, response_json):
        # Do not continue if we've hit the total pages
        logger.info(
            f"Current page: {response_json['page']}, Total pages: {self.num_pages}"
        )
        if self.num_pages:
            return response_json["page"] <= self.num_pages
        return True

    def get_batch_data(self, response_json):
        # Takes the raw API response from calling `get` on the endpoint, and returns
        # the list of records to process.
        if response_json:
            self.num_pages = response_json.get("numPages", 1)
            return response_json.get("results")
        return None

    def get_media_type(self, record: dict):
        # For a given record json, return the media type it represents.
        return constants.AUDIO

    @staticmethod
    def get_title(data: dict) -> str:
        # For a given record, construct a title similar to the one available in the
        # website itself. This is a concatenation of the english name and the species.
        # E.g. Barnacle Goose (Branta leucopsis)
        parts = [data.get("gen", ""), data.get("sp", ""), data.get("ssp", "")]
        scientific = " ".join([p for p in parts if p])
        english = data["en"]
        return f"{english} ({scientific})"

    @staticmethod
    def get_meta_data(data: dict) -> dict:
        # Pull out any other relevant data from the record
        return {
            "country": data.get("cnt"),
            "location": data.get("loc"),
            "latitude": data.get("lat"),
            "longitude": data.get("lng"),
        }

    @staticmethod
    def get_duration(data: dict) -> int:
        # Pull out the duration of the recording in milliseconds
        # This comes in the form of "MM:SS" from the API
        duration_time = datetime.strptime(data.get("length"), "%M:%S")
        duration = timedelta(minutes=duration_time.minute, seconds=duration_time.second)
        return int(duration.total_seconds() * 1000)

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        # Parse out the necessary info from the record data into a dictionary.

        # If a required field is missing, return early to prevent unnecessary
        # processing.
        if not (foreign_identifier := data.get("id")):
            return None

        if not (foreign_landing_url := data.get("url")):
            return None
        # This comes in the form of "//xeno-canto.org/12345" from the API
        foreign_landing_url = f"https:{foreign_landing_url}"

        if not (url := data.get("file")):
            return None

        # Use the `get_license_info` utility to get license information from a URL.
        license_url = data.get("lic")
        license_info = get_license_info(f"https:{license_url}")
        if license_info is None:
            return None

        # OPTIONAL FIELDS
        # Obtain as many optional fields as possible.
        filetype = data.get("file-name", "").split(".")[-1]
        creator = data.get("rec")
        sample_rate = int(data.get("smp"))
        duration = XenoCantoDataIngester.get_duration(data)
        title = XenoCantoDataIngester.get_title(data)
        meta_data = XenoCantoDataIngester.get_meta_data(data)

        # MEDIA TYPE-SPECIFIC FIELDS
        # Each Media type may also have its own optional fields. See documentation.
        # TODO: Populate media type-specific fields.
        # If your provider supports more than one media type, you'll need to first
        # determine the media type of the record being processed.
        #
        # Example:
        # media_type = self.get_media_type(data)
        # media_type_specific_fields = self.get_media_specific_fields(media_type, data)
        #
        # If only one media type is supported, simply extract the fields here.

        return {
            "foreign_landing_url": foreign_landing_url,
            "url": url,
            "license_info": license_info,
            # Optional fields
            "foreign_identifier": foreign_identifier,
            "filetype": filetype,
            "creator": creator,
            "title": title,
            "meta_data": meta_data,
            "sample_rate": sample_rate,
            "duration": duration,
        }


def main():
    # Allows running ingestion from the CLI without Airflow running for debugging
    # purposes.
    ingester = XenoCantoDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
