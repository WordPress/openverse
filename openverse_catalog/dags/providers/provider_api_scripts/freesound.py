"""
Content Provider:       Freesound

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image, the respective
                        meta-data.

Notes:                  https://freesound.org/docs/api/
                        Rate limit: No limit for our API key.
                        This script can be run either to ingest the full dataset or
                        as a dated DAG.
"""
import functools
import logging
from datetime import datetime

import requests
from airflow.models import Variable
from common import constants
from common.licenses.licenses import get_license_info
from common.loader import provider_details as prov
from common.requester import RetriesExceeded
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester
from requests.exceptions import ConnectionError, SSLError
from retry import retry


logger = logging.getLogger(__name__)


class FreesoundDataIngester(ProviderDataIngester):
    batch_limit = 150
    delay = 5  # TODO: Remove after full Freesound run
    host = "freesound.org"
    endpoint = f"https://{host}/apiv2/search/text"
    providers = {"audio": prov.FREESOUND_DEFAULT_PROVIDER}
    flaky_exceptions = (SSLError, ConnectionError)
    preferred_preview = "preview-hq-mp3"
    preview_bitrates = {
        "preview-hq-mp3": 128000,
        "preview-lq-mp3": 64000,
        "preview-hq-ogg": 192000,
        "preview-lq-ogg": 80000,
    }

    def __init__(self, *args, **kwargs):
        self.api_key = Variable.get("API_KEY_FREESOUND")
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Token {self.api_key}",
        }

        super().__init__(*args, **kwargs)

    def get_media_type(self, record: dict) -> str:
        return constants.AUDIO

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            start_date = "*"
            # Allow self.date to be undefined, necessary for the first full, successful
            # run of Freesound but can be changed to dated afterwards.
            if self.date:
                start_date = datetime.strftime(
                    datetime.fromisoformat(self.date), "%Y-%m-%dT%H:%M:%SZ"
                )
            return {
                "format": "json",
                "query": "",
                "page_size": self.batch_limit,
                "fields": ",".join(
                    [
                        "id",
                        "url",
                        "name",
                        "tags",
                        "description",
                        "created",
                        "license",
                        "type",
                        "download",
                        "filesize",
                        "bitrate",
                        "bitdepth",
                        "duration",
                        "samplerate",
                        "pack",
                        "username",
                        "num_downloads",
                        "avg_rating",
                        "num_ratings",
                        "geotag",
                        "previews",
                    ]
                ),
                "filter": f"created:[{start_date} TO NOW]",
                "page": 1,
            }
        else:
            return {**prev_query_params, "page": prev_query_params["page"] + 1}

    def get_batch_data(self, response_json):
        if results := response_json.get("results"):
            # Freesound sometimes returns results that are just "None", filter these out
            return [item for item in results if item is not None]
        return None

    @staticmethod
    def _get_creator_data(item):
        if creator := item.get("username"):
            creator = creator.strip()
            creator_url = f"https://freesound.org/people/{creator}/"
        else:
            creator_url = None
        return creator, creator_url

    @staticmethod
    def _get_metadata(item):
        metadata = {}
        fields = [
            "description",
            "num_downloads",
            "avg_rating",
            "num_ratings",
            "geotag",
            "download",
        ]
        for field in fields:
            if field_value := item.get(field):
                metadata[field] = field_value
        return metadata

    @staticmethod
    def _get_license(item):
        item_license = get_license_info(license_url=item.get("license"))

        if item_license.license is None:
            return None
        return item_license

    @functools.lru_cache(maxsize=1024)
    def _get_set_info(self, set_url):
        try:
            response_json = self.get_response_json(
                query_params={},
                endpoint=set_url,
            )
            set_id = response_json.get("id")
            set_name = response_json.get("name")
            return set_id, set_name
        except RetriesExceeded:
            # https://github.com/WordPress/openverse-catalog/issues/659
            # This should be temporary for the full run of Freesound, as
            # some historical audio sets 404.
            logger.warning("Unable to fetch audio_set information")
            return None, None

    def _get_audio_set_info(self, media_data):
        # set id, set name, set url
        set_url = media_data.get("pack")
        if set_url is not None:
            set_id, set_name = self._get_set_info(set_url)
            return set_id, set_name, set_url
        else:
            return None, None, None

    @retry(flaky_exceptions, tries=3, delay=1, backoff=2)
    def _get_audio_file_size(self, url):
        """
        Get the content length of a provided URL.

        Freesound can be finicky, so we want to retry it a few times on
        these conditions:
          * SSLError - 'EOF occurred in violation of protocol (_ssl.c:1129)'
          * ConnectionError - '[Errno 113] No route to host'

        Both of these seem transient and may be the result of some odd behavior on the
        Freesound API end. We have an API key that's supposed to be maxed out, so
        I can't imagine it's throttling (aetherunbound).

        TODO(obulat): move filesize detection to the polite crawler
        """
        return int(requests.head(url).headers["content-length"])

    def _get_audio_files(
        self, media_data
    ) -> tuple[dict, list[dict]] | tuple[None, None]:
        previews = media_data.get("previews")
        # If there are no previews, then we will not be able to play the file
        if not previews:
            return None, None

        # If our preferred preview type is not present, skip this audio
        if not (preview_url := previews.get(self.preferred_preview)):
            return None, None

        main_file = {
            "audio_url": preview_url,
            "filetype": self.preferred_preview.split("-")[-1],
            "bit_rate": FreesoundDataIngester.preview_bitrates[self.preferred_preview],
            "filesize": self._get_audio_file_size(preview_url),
        }
        # These are the original files, needs auth for downloading.
        # bit_rate in kilobytes, converted to bytes
        alt_files = [
            {
                "url": media_data.get("download"),
                "bit_rate": int(media_data.get("bitrate")) * 1000,
                "sample_rate": int(media_data.get("samplerate")),
                "filetype": media_data.get("type"),
                "filesize": media_data.get("filesize"),
            }
        ]
        return main_file, alt_files

    def get_record_data(self, media_data: dict) -> dict | list[dict] | None:
        """
        Extract metadata about the audio file.

        Freesound does not have audio thumbnails.
        """
        foreign_landing_url = media_data.get("url")
        if not foreign_landing_url:
            return None

        foreign_identifier = media_data.get("id")
        if not foreign_identifier:
            return None

        item_license = self._get_license(media_data)
        if item_license is None:
            return None

        # We use the mp3-hq preview url as `audio_url` as the main url
        # for playing on the frontend,
        # and the actual uploaded file as an alt_file that is available
        # for download (and requires a user to be authenticated to download)
        try:
            main_audio, alt_files = self._get_audio_files(media_data)
        except self.flaky_exceptions:
            logger.warning(
                f"Unable to get file size for {foreign_landing_url}, skipping"
            )
            return None
        if main_audio is None:
            return None

        creator, creator_url = self._get_creator_data(media_data)
        duration = int(media_data.get("duration") * 1000)
        set_foreign_id, audio_set, set_url = self._get_audio_set_info(media_data)
        return {
            "title": media_data.get("name"),
            "creator": creator,
            "creator_url": creator_url,
            "foreign_identifier": foreign_identifier,
            "foreign_landing_url": foreign_landing_url,
            "duration": duration,
            "license_info": item_license,
            "meta_data": self._get_metadata(media_data),
            "raw_tags": media_data.get("tags"),
            "set_foreign_id": set_foreign_id,
            "audio_set": audio_set,
            "set_url": set_url,
            "alt_files": alt_files,
            # audio_url, filetype, bit_rate
            **main_audio,
        }


def main():
    logger.info("Begin: Freesound provider script")
    ingester = FreesoundDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
