"""
Content Provider:       ccMixter

ETL Process:            Use the API to identify all CC licensed media.

Output:                 TSV file containing the media and the
                        respective meta-data.

Notes:                  Documentation: https://ccmixter.org/query-api
                        ccMixter sends bad JSON and extremely huge headers, both
                        of which need workarounds that are handled by this DAG.
"""

import json
import logging
import re
from typing import Literal

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import DelayedRequester
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)

JSON_OCTALS = re.compile(r":\s*0(?P<num>\d+)\s*(?P<sep>[,}])")


class CcMixterDelayedRequester(DelayedRequester):
    """
    WORKAROUND!

    ccMixter sends bad JSON, including numbers with a leading 0 (observed some
    such cases with "bpm" field). This makes the JSON invalid and raises decode
    errors.

    This class extends ``DelayedRequester`` to supply a custom JSON decoding
    step where we perform a text substitution first and then parse the JSON.
    """

    def _get_json(self, response):
        raw_json = response.text
        cleaned_json = JSON_OCTALS.sub(r":\g<num>\g<sep>", raw_json)
        if cleaned_json == raw_json:
            logger.info("JSON was clean, no substitutions were made.")
        else:
            logger.warning("JSON had bad octals, substitutions were made.")
        try:
            response_json = json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            logger.warning(f"Could not get response_json.\n{e}")
            response_json = None
        return response_json


def patch_http_client():
    """
    WORKAROUND!

    ccMixter sends a very long ``X-Json`` header with the response, which causes
    the ``http.client`` library to raise a ``LineTooLong`` error.

    We work around it by patching the ``_read_headers`` function to ignore the
    line length limit.
    """

    import http.client

    def _read_headers(fp):
        logger.debug("Patched _read_headers() called.")

        headers = []
        while True:
            line = fp.readline()
            headers.append(line)
            if len(headers) > http.client._MAXHEADERS:
                raise http.client.HTTPException(
                    f"got more than {http.client._MAXHEADERS} headers"
                )
            if line in (b"\r\n", b"\n", b""):
                break
        return headers

    http.client._read_headers = _read_headers


class CcMixterDataIngester(ProviderDataIngester):
    providers = {
        "audio": prov.CC_MIXTER_DEFAULT_PROVIDER,
    }
    endpoint = "https://ccmixter.org/api/query/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set-up workarounds!
        patch_http_client()
        self.delayed_requester = CcMixterDelayedRequester(
            delay=self.delay, headers=self.headers
        )

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            # This means this is the first request, so we start with offset 0.
            return {
                "format": "json",
                "limit": self.batch_limit,
                "offset": 0,
            }
        else:
            # This is a subsequent request, so we bump the offset by a value
            # equal to the batch limit.
            return {
                **prev_query_params,
                "offset": prev_query_params["offset"] + self.batch_limit,
            }

    def get_batch_data(self, response_json):
        return response_json

    def get_should_continue(self, response_json):
        # We can know we are at the last page if the number of records returned
        # is less than the batch limit. This is not an issue even if the
        # penultimate page has a batch limit number of results because ccMixter
        # allows paginating after the last page too, returning ``[]``, which is
        # less than the batch limit.
        return len(response_json) >= self.batch_limit

    def get_media_type(self, record: dict) -> Literal["audio"]:
        return constants.AUDIO

    @staticmethod
    def _get_duration(ps: str | None) -> int | None:
        """
        Convert a duration string to the number of milliseconds. This function
        can handle between 1 and 3 segments in the time string.

        :param ps: the human-friendly duration string
        :return: the number of milliseconds
        """

        if not ps:
            return None

        segments = map(int, [0, 0] + ps.split(":"))
        *_, hours, minutes, seconds = segments
        return (hours * 3600 + minutes * 60 + seconds) * 1000

    @staticmethod
    def _get_sample_rate(sr: str | None) -> int | None:
        """
        Convert the sample rate from a human-friendly string to the integer
        number of samples per second.

        :param sr: the human-friendly sample rate
        :return: the number of samples per second
        """

        return int(float(sr.rstrip("k")) * 1000) if sr else None

    def _get_audio_files(
        self, files: list[dict]
    ) -> tuple[dict, list[dict]] | tuple[None, None]:
        """
        Filter the audio files from the file list and identify the main one.

        The list of files can include archives like ZIP files, which we drop.
        The smallest audio file is assumed to be the main one, which is usually
        MP3 in the case of ccMixter.

        :param files: the list of files supplied by ccMixter
        :return: the main file and a list of alternative files
        """

        files = [
            {
                "url": file["download_url"],
                "filesize": file["file_rawsize"],
                "filetype": file["file_format_info"]["default-ext"],
                "sample_rate": self._get_sample_rate(
                    file["file_format_info"].get("sr")
                ),
                "duration": self._get_duration(file["file_format_info"].get("ps")),
            }
            for file in files
            if file["file_format_info"]["media-type"] == "audio"
        ]
        if not files:
            return None, None

        main_file, *alt_files = sorted(files, key=lambda file: file["filesize"])
        return main_file, alt_files

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        if not (foreign_identifier := data.get("upload_id")):
            logger.warning("Rejected record with no foreign identifier.")
            return None

        if not (foreign_landing_url := data.get("file_page_url")):
            logger.warning(
                f"Rejected record {foreign_identifier} with no foreign landing URL."
            )
            return None

        # Use the `get_license_info` utility to get license information from a URL.
        license_url = data.get("license_url")
        license_info = get_license_info(license_url)
        if not license_info:
            logger.warning(
                f"Rejected record {foreign_identifier} with no license info."
            )
            return None

        if not (files := data.get("files")):
            return None
        main_file, alt_files = self._get_audio_files(files)
        if not main_file:
            logger.warning(
                f"Rejected record {foreign_identifier} with no main audio file."
            )
            return None

        # Optional fields

        creator = data.get("user_real_name")
        creator_url = data.get("artist_page_url")
        title = data.get("upload_name")
        meta_data = {
            "description": data.get("upload_description_plain"),
            "description_html": data.get("upload_description_html"),
        }

        # ccMixter tags are comma-separated, and there is a leading and trailing
        # comma, so we need to filter out empty strings.
        raw_tags = list(filter(None, data.get("upload_tags").split(",")))

        return {
            "foreign_identifier": foreign_identifier,
            "foreign_landing_url": foreign_landing_url,
            "license_info": license_info,
            # Optional fields
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "meta_data": meta_data,
            "raw_tags": raw_tags,
            "alt_files": alt_files,
            # ``main_file`` contains the following fields:
            # - ``url``
            # - ``filesize``
            # - ``filetype``
            # - ``sample_rate``
            # - ``duration``
            **main_file,
        }


def main():
    # Allows running ingestion from the CLI without Airflow running for debugging
    # purposes.
    ingester = CcMixterDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
