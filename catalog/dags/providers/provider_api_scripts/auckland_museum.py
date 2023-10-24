"""
TODO: This doc string will be used to generate documentation for the DAG in
DAGs.md. Update it to include any relevant information that you'd like to
be documented.

Content Provider:       AucklandMuseum

ETL Process:            Use the API to identify all CC licensed media.

Output:                 TSV file containing the media and the
                        respective meta-data.

Notes:                  https://api.aucklandmuseum.com/
"""
import logging

from common.constants import IMAGE
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class AucklandMuseumDataIngester(ProviderDataIngester):
    """
    This is a template for a ProviderDataIngester.

    Methods are shown with example implementations. Adjust them to suit your API.
    Resource:
    - https://api.aucklandmuseum.com/
    - https://github.com/AucklandMuseum/API/wiki/Tutorial
    """

    providers = {
        "image": prov.AUCKLAND_MUSEUM_IMAGE_PROVIDER,
    }
    endpoint = "https://api.aucklandmuseum.com/search/collectionsonline/_search"

    delay = 4
    from_start = 0
    total_amount_of_data = 10000

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        # On the first request, `prev_query_params` will be `None`. We can detect this
        # and return our default params.
        if not prev_query_params:
            # Return default query params on the first request
            # primaryRepresentation contain a image url for each data
            # "+" is a query string syntax for must be present
            # copyright:CC state Creative Commons Attribution 4.0
            return {
                "q": "_exists_:primaryRepresentation+copyright:CC",
                "size": "100",
                "from": self.from_start,
            }
        else:
            # Increment `from` by 100.
            return {
                **prev_query_params,
                "from": prev_query_params["from"] + 100,
            }

    def get_batch_data(self, response_json):
        # Takes the raw API response from calling `get` on the endpoint, and returns
        # the list of records to process.
        if response_json:
            return response_json.get("hits").get("hits")
        return None

    def get_should_continue(self, response_json):
        # Do not continue if we have exceeded the total amount of data
        if self.from_start >= self.total_amount_of_data:
            logger.info(
                "The final amount of data has been processed. Halting ingestion."
            )
            return False

        return True

    def get_media_type(self, record: dict):
        return IMAGE

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        # Parse out the necessary info from the record data into a dictionary.
        # TODO: Update based on your API.
        # TODO: Important! Refer to the most up-to-date documentation about the
        # available fields in `openverse_catalog/docs/data_models.md`

        # REQUIRED FIELDS:
        # - foreign_identifier
        # - foreign_landing_url
        # - license_info
        # - url
        #
        # If a required field is missing, return early to prevent unnecessary
        # processing.
        if not (foreign_identifier := data.get("foreign_id")):
            return None

        if not (foreign_landing_url := data.get("foreign_landing_url")):
            return None

        if not (url := data.get("url")):
            return None

        # Use the `get_license_info` utility to get license information from a URL.
        license_url = data.get("license")
        license_info = get_license_info(license_url)
        if license_info is None:
            return None

        # OPTIONAL FIELDS
        # Obtain as many optional fields as possible.
        thumbnail_url = data.get("thumbnail")
        filesize = data.get("filesize")
        filetype = data.get("filetype")
        creator = data.get("creator")
        creator_url = data.get("creator_url")
        title = data.get("title")
        meta_data = data.get("meta_data")
        raw_tags = data.get("tags")
        watermarked = data.get("watermarked")

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
            "thumbnail_url": thumbnail_url,
            "filesize": filesize,
            "filetype": filetype,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "meta_data": meta_data,
            "raw_tags": raw_tags,
            "watermarked": watermarked,
            # TODO: Remember to add any media-type specific fields here
        }


def main():
    # Allows running ingestion from the CLI without Airflow running for debugging
    # purposes.
    ingester = AucklandMuseumDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
