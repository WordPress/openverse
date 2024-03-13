import abc
import logging
import os
from datetime import datetime

from common import urls
from common.extensions import extract_filetype
from common.loader import provider_details as prov
from common.storage.tsv_columns import CURRENT_VERSION


logger = logging.getLogger(__name__)

# Filter out tags that exactly match these terms. All terms should be lowercase.
TAG_DENYLIST = {
    "flickriosapp:filter=flamingo",
    "no person",
    "undefined",
    "uploaded:by=flickrmobile",
    "uploaded:by=instagram",
    "squareformat",
}

# Filter out tags that contain the following terms. All entrées should be lowercase.
TAG_CONTAINS_DENYLIST = {
    "flickriosapp",
    "uploaded",
    ":",
    "=",
    "cc0",
    "by",
    "by-nc",
    "by-nd",
    "by-sa",
    "by-nc-nd",
    "by-nc-sa",
    "pdm",
}

COMMON_CRAWL = "commoncrawl"
PROVIDER_API = "provider_api"

FILETYPE_EQUIVALENTS = {"jpeg": "jpg", "tif": "tiff"}
PG_INTEGER_MAXIMUM = 2147483647


class MediaStore(metaclass=abc.ABCMeta):
    """
    An abstract base class that stores media information from a given provider.

    Optional init arguments:
    provider:       String marking the provider in the `media`
                    (`image`, `audio` etc) table of the DB.
    tsv_suffix:     Optional string to append to the tsv filename.
    buffer_length:  Integer giving the maximum number of media information rows
                    to store in memory before writing them to disk.
    strip_url_trailing_slashes: Boolean to strip trailing slashes from URLs during
                                validation
    """

    def __init__(
        self,
        provider: str | None = None,
        tsv_suffix: str | None = None,
        buffer_length: int = 100,
        media_type: str | None = "generic",
        strip_url_trailing_slashes: bool = True,
    ):
        logger.info(f"Initialized {media_type} MediaStore with provider {provider}")
        self.media_type = media_type
        self.provider = provider
        self.buffer_length = buffer_length
        self.strip_url_trailing_slashes = strip_url_trailing_slashes
        self.output_path = self._initialize_output_path(provider, tsv_suffix=tsv_suffix)
        self.columns = None
        self._media_buffer = []
        self._total_items = 0

    def save_item(self, media) -> None:
        """
        Append item data to the buffer as a tsv row, only if data is valid.

        Args:
            media: a namedtuple with validated media metadata
        """
        tsv_row = self._create_tsv_row(media)
        if tsv_row:
            self._media_buffer.append(tsv_row)
            self._total_items += 1
        if len(self._media_buffer) >= self.buffer_length:
            self._flush_buffer()

    @abc.abstractmethod
    def add_item(self, **kwargs):
        """Abstract method to clean the item data and add it to the store."""
        pass

    def clean_media_metadata(self, **media_data) -> dict | None:
        """
        Clean and enrich the base media metadata common for all media types.

        Even though we clean license info in the provider API scripts,
        we validate it here, too, to make sure we don't have
        invalid license information in the database.

        Returns a dictionary: media_type-specific fields are untouched,
        and for common metadata we:
        - validate `filetype`
        - validate `url`, `foreign_landing_url`, `thumbnail_url`, and `creator_url`
          (stripping trailing slashes if requested)
        - enrich `metadata`,
        - replace `raw_tags` with enriched `tags`,
        - validate `source`,
        - add `provider`,
        - add default `category`, if available.

        Raises an error if missing any of the required fields:
        `license_info`, `foreign_identifier`, `foreign_landing_url`, or `url`.
        """
        for field in [
            "license_info",
            "foreign_identifier",
            "foreign_landing_url",
            "url",
        ]:
            if media_data.get(field) is None:
                raise ValueError(f"Record missing required field: `{field}`")

        for field in [
            "url",
            "foreign_landing_url",
            "thumbnail_url",
            "creator_url",
        ]:
            if field not in media_data:
                continue
            media_data[field] = urls.validate_url_string(
                media_data[field],
                self.strip_url_trailing_slashes,
            )
        media_data["source"] = self._get_source(media_data.get("source"), self.provider)
        # Add ingestion_type column value based on `source`.
        # The implementation is based on `ingestion_column`
        if media_data.get("ingestion_type") is None:
            if media_data["source"] == "commoncrawl":
                media_data["ingestion_type"] = "commoncrawl"
            else:
                media_data["ingestion_type"] = "provider_api"

        media_data["filetype"] = self._validate_filetype(
            media_data["filetype"], media_data["url"]
        )
        media_data["filesize"] = self._validate_integer(media_data.get("filesize"))

        media_data["tags"] = self._enrich_tags(media_data.pop("raw_tags", None))
        media_data["meta_data"] = self._enrich_meta_data(
            media_data.pop("meta_data", None),
            media_data["license_info"].url,
            media_data["license_info"].raw_url,
        )
        media_data["license_"] = media_data["license_info"].license
        media_data["license_version"] = media_data["license_info"].version

        media_data.pop("license_info", None)
        media_data["provider"] = self.provider
        media_data["category"] = media_data[
            "category"
        ] or prov.DEFAULT_IMAGE_CATEGORY.get(self.provider)
        return media_data

    def commit(self):
        """Write all remaining media items in the buffer to disk."""
        self._flush_buffer()
        return self.total_items

    def _initialize_output_path(
        self,
        provider: str | None,
        tsv_suffix: str | None = None,
        version: str | None = None,
    ) -> str:
        """
        Create the path for the tsv file.

        If output_dir and output_file ar not given,
        the following filename is used:
        `/tmp/{provider_name}_{media_type}_{timestamp}.tsv`

        Returns:
            Path of the tsv file to write media data pulled from providers
        """

        output_dir = os.getenv("OUTPUT_DIR")
        if output_dir is None:
            logger.warning(
                "OUTPUT_DIR is not set in the environment. Output will go to /tmp."
            )
            output_dir = "/tmp"
        version = f"v{version or CURRENT_VERSION[self.media_type]}"

        path_components = [
            provider,
            self.media_type,
            version,
            datetime.now().strftime("%Y%m%d%H%M%S"),
            tsv_suffix,
        ]
        output_file = ("_").join(filter(None, path_components)) + ".tsv"

        output_path = os.path.join(output_dir, output_file)
        logger.info(f"Output path: {output_path}")
        return output_path

    @property
    def total_items(self):
        """Get total items for directly using in scripts."""
        return self._total_items

    def _create_tsv_row(self, item):
        row_length = len(self.columns)
        prepared_strings = [
            self.columns[i].prepare_string(item[i]) for i in range(row_length)
        ]
        logger.debug(f"Prepared strings list:\n{prepared_strings}")
        for i in range(row_length):
            if self.columns[i].required and prepared_strings[i] is None:
                logger.warning(f"Row missing required {self.columns[i].name}")
                return None
        else:
            return (
                "\t".join([s if s is not None else "\\N" for s in prepared_strings])
                + "\n"
            )

    def _flush_buffer(self) -> int:
        buffer_length = len(self._media_buffer)
        if buffer_length > 0:
            logger.info(f"Writing {buffer_length} lines from buffer to disk.")
            with open(self.output_path, "a") as f:
                f.writelines(self._media_buffer)
                self._media_buffer = []
                logger.debug(
                    f"Total Media Items Processed so far:  {self._total_items}"
                )
        else:
            logger.debug("Empty buffer!  Nothing to write.")
        return buffer_length

    @staticmethod
    def _tag_denylisted(tag: str | dict) -> bool:
        """
        Determine if the tag is banned or contains a banned substring.

        :param tag: the tag to be verified against the blacklist
        :return: true if tag is blacklisted, else returns false
        """
        if isinstance(tag, dict):  # check if the tag is already enriched
            tag = tag.get("name")
        if tag in TAG_DENYLIST:
            return True
        for denylisted_substring in TAG_CONTAINS_DENYLIST:
            if denylisted_substring in tag:
                return True
        return False

    @staticmethod
    def _enrich_meta_data(meta_data, license_url, raw_license_url) -> dict:
        """Ensure that meta_data is a dict and contains both license URLs."""
        if not isinstance(meta_data, dict):
            logger.debug(f"`meta_data` is not a dictionary: {meta_data}")
            enriched_meta_data = {
                "license_url": license_url,
                "raw_license_url": raw_license_url,
            }
        else:
            enriched_meta_data = meta_data
            enriched_meta_data.update(
                license_url=license_url, raw_license_url=raw_license_url
            )
        return enriched_meta_data

    def _enrich_tags(self, raw_tags) -> list | None:
        """
        Add provider information to tags.

        Args:
            raw_tags: List of strings or dictionaries

        Returns:
            A list of 'enriched' tags:
            {"name": "tag_name", "provider": self._PROVIDER}
        """
        if not isinstance(raw_tags, list):
            logger.debug("`tags` is not a list.")
            return None
        else:
            return [
                self._format_raw_tag(tag)
                for tag in raw_tags
                if not self._tag_denylisted(tag)
            ]

    def _format_raw_tag(self, tag):
        if isinstance(tag, dict) and tag.get("name") and tag.get("provider"):
            logger.debug(f"Tag already enriched: {tag}")
            return tag
        else:
            logger.debug(f"Enriching tag: {tag}")
            return {"name": tag, "provider": self.provider}

    def _validate_filetype(self, filetype: str | None, url: str) -> str | None:
        """
        Extract filetype from the media URL if filetype is None.

        Unifies filetypes that have variants such as jpg/jpeg and tiff/tif.
        :param filetype: Optional filetype string.
        :return: filetype string or None
        """
        if filetype is None:
            filetype = extract_filetype(url, self.media_type)
        if self.media_type != "image":
            return filetype
        return FILETYPE_EQUIVALENTS.get(filetype, filetype)

    @staticmethod
    def _validate_integer(value: int | None) -> int | None:
        """
        Ensure the provided int value is less than the Postgres maximum integer value.

        If the value exceeds this maximum, None is returned.
        TODO: Remove this logic once the column has been embiggened
        https://github.com/WordPress/openverse-catalog/issues/730
        https://github.com/WordPress/openverse-catalog/issues/873
        """
        if value and value >= PG_INTEGER_MAXIMUM:
            logger.warning(f"Value exceeds Postgres maximum integer value: {value}")
            return None
        return value

    @staticmethod
    def _get_source(source, provider):
        """Return `source` if given, otherwise `provider`."""
        if not source:
            source = provider

        return source
