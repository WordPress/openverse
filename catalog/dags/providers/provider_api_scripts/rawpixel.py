"""
Content Provider:       Rawpixel

ETL Process:            Use the API to identify all CC-licensed images.

Output:                 TSV file containing the image meta-data.

Notes:                  Rawpixel has given Openverse beta access to their API.
                        This API is undocumented, and we will need to contact Rawpixel
                        directly if we run into any issues.
                        The public API max results range is limited to 100,000 results,
                        although the API key we've been given can circumvent this limit.
                        https://www.rawpixel.com/api/v1/search?tags=$publicdomain&page=1&pagesize=100
"""
import base64
import hmac
import html
import logging
import re
from urllib.parse import urlencode

from airflow.models import Variable

from common import constants
from common.licenses import get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class RawpixelDataIngester(ProviderDataIngester):
    providers = {constants.IMAGE: prov.RAWPIXEL_DEFAULT_PROVIDER}
    api_path = "/api/v1/search"
    endpoint = f"https://www.rawpixel.com{api_path}"
    # Regex pattern for partial suffix capture
    suffix_pattern_partial = re.compile(
        r"""
            # Any text ending in free or original
            (?:free\ ?|original\ ?)?
            # Optionally "free public" or "original public"
            (?:public
                # Optionally "public domain"
                (?:\ domain
                    # Optionally "original public domain CC0 photo"
                    # or "free public domain CC0 image"
                    (?:\ CC0\ (?:image|photo))?
                )?
            )?
            # Could end in punctuation, but the string must end with this sequence
            [.,!?]?$
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )
    # Regex pattern for full suffix capture
    suffix_pattern_full = re.compile(
        r"""
            # Capture any of these complete endings
            (?:
                Free\ public\ domain\ CC0\ (?:image|photo) |
                Digitally\ enhanced\ by\ rawpixel
            )
            # Could end in punctuation, but the string must end with this sequence
            [.,!?]?$
        """,
        flags=re.IGNORECASE | re.VERBOSE,
    )
    # Keywords which could be present in tags meaning they should be excluded
    tags_exclude_list = {
        "cc0",
        "creative commons",
        "public domain",
    }
    # Image size options, without watermark.
    full_size_option = "editor_1024" # Always serve webp format, "image_1000" can be used as an alternative with jpeg fallback
    png_full_size_option = "image_png_1300" # Serve webp format if accepted else jpeg
    png_dark_full_size_option = "dark_image_png_1300" # Serve webp format if accepted else jpeg
    thumbnail_size_option = "image_600" # Serve webp format if accepted else jpeg
    png_thumbnail_size_option = "image_png_600" # Serve webp format if accepted else jpeg
    png_dark_thumbnail_size_option = "dark_image_png_600" # Serve webp format if accepted else jpeg

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key: str = Variable.get("API_KEY_RAWPIXEL")

    def get_media_type(self, record: dict) -> str:
        return constants.IMAGE

    def _get_signature(self, query_params: dict) -> str:
        """
        Get the query signature for a request.

        URL encode the ordered parameters in a way that matches Node's
        querystring.stringify as closely as possible
        See: https://docs.python.org/3.10/library/urllib.parse.html#urllib.parse.urlencode
        and https://nodejs.org/api/querystring.html#querystringstringifyobj-sep-eq-options
        """  # noqa: E501
        # Params must be ordered for deterministic computation
        ordered_params = {k: v for k, v in sorted(query_params.items())}
        # Build parameters as a string, split out sequences since that's Node's behavior
        query = urlencode(ordered_params, doseq=True)
        # Concat onto API path, note that the scheme & fqdn are intentionally missing
        url = f"{self.api_path}?{query}"
        # Set up an HMAC using our API key and the URL as a message
        digest = hmac.digest(
            key=self.api_key.encode("utf-8"),
            msg=url.encode("utf-8"),
            digest="sha256",
        )
        # Encode it as base64
        b64 = base64.b64encode(digest)
        # Perform some character replacements, this logic was supplied explicitly by
        # Rawpixel's Node example
        signature = b64.replace(b"+", b"-").replace(b"/", b"_").replace(b"=", b"")
        # Convert back to a string
        return signature.decode("utf-8")

    def get_next_query_params(self, prev_query_params: dict | None, **kwargs) -> dict:
        if not prev_query_params:
            params = {
                "tags": "$publicdomain",
                "page": 1,
                "pagesize": self.batch_limit,
            }
        else:
            params = {**prev_query_params, "page": prev_query_params["page"] + 1}
            # Remove signature
            params.pop("s", None)
        # Inject HMAC signature after all params have been added
        return {**params, "s": self._get_signature(params)}

    def get_batch_data(self, response_json):
        if response_json and (results := response_json.get("results")):
            return results
        return None

    @staticmethod
    def _get_full_size_preset(self, data: dict) -> str | None:
        """Get the full size preset based on the image properties."""
        if data.get("isPng"):
            if data.get("isDarkPng"):
                return RawpixelDataIngester.png_dark_full_size_option
            return RawpixelDataIngester.png_full_size_option
        return RawpixelDataIngester.full_size_option

    @staticmethod
    def _get_thumbnail_size_preset(self, data: dict) -> str | None:
        """Get the full size preset based on the thumbnail properties."""
        if data.get("isPng"):
            if data.get("isDarkPng"):
                return RawpixelDataIngester.png_dark_thumbnail_size_option
            return RawpixelDataIngester.png_thumbnail_size_option
        return RawpixelDataIngester.thumbnail_size_option

    @staticmethod
    def _get_image_url(data: dict, size_option: str) -> str | None:
        """
        Get the URL for an image.

        Rawpixel provides a "style_uri" string which can be formatted with these values:
            'image_24', 'image_png_24', 'image_48', 'image_png_48', 'image_100',
            'image_png_100', 'image_150', 'image_png_150', 'image_200', 'image_png_200',
            'image_250', 'image_png_250', 'image_300', 'image_png_300', 'image_400',
            'image_png_400', 'image_500', 'image_png_500', 'image_600', 'image_png_600',
            'image_700', 'image_png_700', 'image_800', 'image_png_800', 'image_900',
            'image_png_900', 'image_1000', 'image_png_1000', 'image_1300',
            'image_png_1300', 'editor_1024'

        The number refers to the width displayed, and a png option is provided for each
        size.

        Note that preset size starting from 1100 are watermarked.
        """
        style_uri = data.get("style_uri")
        if not style_uri:
            return None
        return style_uri.format(size_option)

    @staticmethod
    def _get_image_properties(data: dict) -> tuple[None, None] | tuple[int, int]:
        width = max(data.get("width", 0), data.get("display_image_width", 0))
        height = max(data.get("height", 0), data.get("display_image_height", 0))
        if (width, height) == (0, 0):
            return None, None
        return width, height

    @staticmethod
    def _clean_text(text: str) -> str:
        # Clean whitespace
        text = text.strip()
        # First clear full patterns
        text = RawpixelDataIngester.suffix_pattern_full.sub("", text)
        # Then clear partial patterns
        text = RawpixelDataIngester.suffix_pattern_partial.sub("", text)
        # Unescape HTMl sequences
        text = html.unescape(text)
        # Clean whitespace once more
        text = text.strip()
        # Remove any trailing commas
        text = text.removesuffix(",")
        return text

    @staticmethod
    def _get_title(metadata: dict) -> str | None:
        """
        Get the title for an image.

        Titles come in the following form, so we clean them up a bit:
          Bull elk searches for food | Free Photo - rawpixel
          Desktop wallpaper summer beach landscape, | Free Photo - rawpixel
          Branch with a sunflower (1714&ndash;1760) | Free Photo Illustration - rawpixel
          Free public domain CC0 photo. | Free Photo - rawpixel
          Flower background. Free public domain | Free Photo - rawpixel
        """
        title: str = metadata.get("title")
        if not title:
            return None
        # Cut off the last bit about Rawpixel
        title = title.split("|", maxsplit=1)[0].strip()
        # Clean text
        title = RawpixelDataIngester._clean_text(title)
        # Remove trailing periods
        title = title.removesuffix(".")
        return title or None

    @staticmethod
    def _get_meta_data(data: dict, metadata: dict) -> dict:
        description = RawpixelDataIngester._clean_text(
            metadata.get("description_text") or ""
        )
        meta_data = {
            "description": description or None,
            "download_count": data.get("download_count"),
        }
        meta_data = {k: v for k, v in meta_data.items() if v is not None}
        return meta_data

    @staticmethod
    def _get_creator(data: dict) -> str | None:
        source = data.get("artist_names", "")
        source = source.removesuffix("(Source)").strip()
        return source or None

    @staticmethod
    def _get_tags(metadata: dict) -> list[str]:
        keywords = metadata.get("popular_keywords")
        if keywords:
            return [
                keyword
                for keyword in keywords
                if not any(
                    exclude_tag in keyword
                    for exclude_tag in RawpixelDataIngester.tags_exclude_list
                )
            ]
        return []

    @staticmethod
    def _get_category(metadata: dict) -> str | None:
        keywords = set(metadata.get("popular_keywords", []))
        if "public domain art" in keywords:
            return prov.ImageCategory.DIGITIZED_ARTWORK
        if "image" in keywords or "photo" in keywords:
            return prov.ImageCategory.PHOTOGRAPH
        if "clipart" in keywords:
            return prov.ImageCategory.ILLUSTRATION
        return None

    def get_record_data(self, data: dict) -> dict | list[dict] | None:
        # verify the license and extract the metadata
        if not (foreign_identifier := data.get("id")):
            return None

        if not (foreign_landing_url := data.get("url")):
            return None

        if not (metadata := data.get("metadata")):
            return None

        if not (license_info := get_license_info(metadata["licenseUrl"])):
            return None

        full_size_preset = self._get_full_size_preset(self, data)
        if not (url := self._get_image_url(data, full_size_preset)):
            return None

        thumbnail_preset = self._get_thumbnail_size_preset(self, data)
        if not (thumbnail_url := self._get_image_url(data, thumbnail_preset)):
            thumbnail_url = None

        width, height = self._get_image_properties(data)
        return {
            "foreign_landing_url": foreign_landing_url,
            "url": url,
            "thumbnail_url": thumbnail_url,
            "license_info": license_info,
            "foreign_identifier": foreign_identifier,
            "width": width,
            "height": height,
            "title": self._get_title(metadata),
            "meta_data": self._get_meta_data(data, metadata),
            "raw_tags": self._get_tags(metadata),
            "creator": self._get_creator(data),
            "filetype": data.get("name_ext"),
            # Filesize not available via the API and wouldn't reflect final image size
            # anyway since we reference reduced-sized images
            "category": self._get_category(metadata),
        }


def main():
    ingester = RawpixelDataIngester()
    ingester.ingest_records()


if __name__ == "__main__":
    main()
