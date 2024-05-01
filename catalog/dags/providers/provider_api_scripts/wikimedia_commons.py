"""
**Content Provider:** Wikimedia Commons

**ETL Process:** Use the API to identify all CC-licensed images.

**Output:** TSV file containing the image, the respective
                        meta-data.

# Notes

Rate limit of no more than 200 requests/second, and we are required to set a unique
User-Agent field ([docs](https://www.mediawiki.org/wiki/Wikimedia_REST_API#Terms_and_conditions)).

Wikimedia Commons uses an implementation of the
[MediaWiki API](https://www.mediawiki.org/wiki/API:Main_page). This API is incredibly
complex in the level of configuration you can provide when querying, and as such it can
also be quite abstruse. The most straightforward docs can be found on the
[Wikimedia website directly](https://commons.wikimedia.org/w/api.php?action=help&modules=query),
as these show all the parameters available. Specifications on queries can also be found
on the [query page](https://www.mediawiki.org/wiki/API:Query).

Different kinds of queries can be made against the API using "modules", we use the
[allimages module](https://www.mediawiki.org/wiki/API:Allimages), which lets us search
for images in a given time range (see `"generator": "allimages"` in the query params).

Many queries will return results in batches, with the API supplying a "continue" token.
This token is used on subsequent calls to tell the API where to start the next set of
results from; it functions as a page offset ([docs](https://www.mediawiki.org/wiki/API:Query#Continuing_queries)).

We can also specify what kinds of information we want for the query. Wikimedia has a
massive amount of data on it, so it only returns what we ask for. The fields that are
returned are defined by the [properties](https://www.mediawiki.org/wiki/API:Properties)
or "props" parameter. Sub-properties can also be defined, with the parameter name of
the sub-property determined by an abbreviation of the higher-level property. For
instance, if our property is "imageinfo" and we want to set sub-property values, we
would define those in "iiprops".

The data within a property is paginated as well, Wikimedia will handle iteration through
the property sub-pages using the "continue" token
([see here for more details](https://www.mediawiki.org/wiki/API:Properties#Additional_notes)).

Depending on the kind of property data that's being returned, it's possible for the API
to iterate extensively on a specific media item. What Wikimedia is iterating over in
these cases can be gleaned from the "continue" token. Those tokens take the form of,
as I understand it, "<primary-iterator>||<next-iteration-prop>", paired with an
"<XX>continue" value for the property being iterated over. For example, if we're
were iterating over a set of image properties, the token might look like:

```
{
    "iicontinue": "The_Railway_Chronicle_1844.pdf|20221209222801",
    "gaicontinue": "20221209222614|NTUL-0527100_英國產業革命史略.pdf",
    "continue": "gaicontinue||globalusage",
}
```

In this case, we're iterating over the "global all images" generator (gaicontinue) as
our primary iterator, with the "image properties" (iicontinue) as the secondary continue
iterator. The "globalusage" property would be the next property to iterate over. It's
also possible for multiple sub-properties to be iterated over simultaneously, in which
case the "continue" token would not have a secondary value (e.g. `gaicontinue||`).

In most runs, the "continue" key will be `gaicontinue||` after the first request, which
means that we have more than one batch to iterate over for the primary iterator. Some
days will have fewer images than the batch limit but still have multiple batches of
content on the secondary iterator, which means the "continue" key may not have a primary
iteration component (e.g. `||globalusage`). This token can also be seen when the first
request has more data in the secondary iterator, before we've processed any data on
the primary iterator.

Occasionally, the ingester will come across a piece of media that has many results for
the property it's iterating over. An example of this can include an item being on many
pages, this it would have many "global usage" results. In order to process the entire
batch, we have to iterate over *all* of the returned results; Wikimedia does not provide
a mechanism to "skip to the end" of a batch. On numerous occasions, this iteration has
been so extensive that the pull media task has hit the task's timeout. To avoid this,
we limit the number of iterations we make for parsing through a sub-property's data. If
we hit the limit, we re-issue the original query *without* requesting properties that
returned large amounts of data. Unfortunately, this means that we will
**not** have that property's data for these items the second time around (e.g.
popularity data if we needed to skip global usage). In the case of popularity,
especially since the problem with these images is that they're so popular, we want to
preserve that information where possible! So we cache the popularity data from
previous iterations and use it in subsequent ones if we come across the same
item again.

Below are some specific references to various properties, with examples for cases where
they might exceed the limit. Technically, it's feasible for almost any property to
exceed the limit, but these are the ones that we've seen in practice.

## `imageinfo`
[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bimageinfo)

[Example where metadata has hundreds of data points](https://commons.wikimedia.org/wiki/File:The_Railway_Chronicle_1844.pdf#metadata)
(see "Metadata" table, which may need to be expanded).

For these requests, we can remove the `metadata` property from the `iiprops` parameter
to avoid this issue on subsequent iterations.

## `globalusage`
[Docs](https://commons.wikimedia.org/w/api.php?action=help&modules=query%2Bglobalusage)

[Example where an image is used on almost every wiki](https://commons.wikimedia.org/w/index.php?curid=4298234).

For these requests, we can remove the `globalusage` property from the `prop` parameter
entirely and eschew the popularity data for these items.
"""  # noqa: E501

import argparse
import logging
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import MappingProxyType

import lxml.html as html

from common.constants import AUDIO, IMAGE
from common.licenses import LicenseInfo, get_license_info
from common.loader import provider_details as prov
from providers.provider_api_scripts.provider_data_ingester import ProviderDataIngester


logger = logging.getLogger(__name__)


class WikimediaCommonsDataIngester(ProviderDataIngester):
    providers = {
        "image": prov.WIKIMEDIA_DEFAULT_PROVIDER,
        "audio": prov.WIKIMEDIA_AUDIO_PROVIDER,
    }
    host = "commons.wikimedia.org"
    endpoint = f"https://{host}/w/api.php"

    # The 10000 is a bit arbitrary, but needs to be larger than the mean
    # number of uses per file (globally) in the response_json, or we will
    # fail without a continuation token.  The largest example seen so far
    # had a little over 1000 uses
    mean_global_usage_limit = 10000
    # Total number of attempts to retrieve global usage pages for a given batch.
    # These can be very large, so we need to limit the number of attempts otherwise
    # the DAG will hit the timeout when it comes across these items.
    # See: https://github.com/WordPress/openverse-catalog/issues/725
    max_page_iteration_before_give_up = 100

    image_mediatypes = {"BITMAP", "DRAWING"}
    audio_mediatypes = {"AUDIO"}
    # Other types available in the API are OFFICE for pdfs and VIDEO

    # The batch_limit applies to the number of pages received by the API, rather
    # than the number of individual records. This means that for Wikimedia Commons
    # setting a global `INGESTION_LIMIT` will still limit the number of records, but
    # the exact limit may not be respected.
    batch_limit = 250

    class ReturnProps:
        """Different sets of properties to return from the API."""

        # All normal media info, plus popularity info by global usage
        query_all = "imageinfo|globalusage"
        # Just media info, used where there's too much global usage data to parse
        query_no_popularity = "imageinfo"

        # All media info we care about
        media_all = "url|user|dimensions|extmetadata|mediatype|size|metadata"
        # Everything minus the metadata, which is only necessary for audio and can
        # balloon for PDFs which are considered images by Wikimedia
        media_no_metadata = "url|user|dimensions|extmetadata|mediatype|size"

    # MappingProxy effectively provides a frozen dictionary, since this is defined
    # at the class level and technically mutable.
    default_props = MappingProxyType(
        {
            "prop": ReturnProps.query_all,
            "iiprop": ReturnProps.media_all,
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.start_timestamp, self.end_timestamp = self.derive_timestamp_pair(self.date)
        self.continue_token = {}
        self.current_props = self.default_props.copy()
        self.popularity_cache: dict[str, int] = {}

    def get_next_query_params(self, prev_query_params: dict | None):
        # NOTE: If more sub-properties are added here, an additional contingency for
        # iterating over that property's "continue" token will need to be added
        # to the `adjust_parameters_for_next_iteration` function, otherwise the
        # ingestion could get stuck in an infinite loop.
        return {
            # The type of action being taken for the API request
            "action": "query",
            # What "generator" to use for returning results, in this case "allimages"
            "generator": "allimages",
            # How to sort the "global all images" (gai) results
            "gaisort": "timestamp",
            # How to order the results
            "gaidir": "newer",
            # The number of "all images" results to return per request
            "gailimit": self.batch_limit,
            # The number of "global usage" results to return per request
            "gulimit": self.batch_limit,
            # What namespace to search in, 0 is the main namespace
            # https://www.mediawiki.org/wiki/Help:Namespaces
            "gunamespace": 0,
            "format": "json",
            # The timestamp to start the search from
            "gaistart": self.start_timestamp,
            # The timestamp to end the search at
            "gaiend": self.end_timestamp,
            # The current properties to use for the request
            **self.current_props,
            # The current continue token to use for the request provided by Wikimedia
            **self.continue_token,
        }

    def get_media_type(self, record):
        """Get the media_type of a parsed Record"""
        return record["media_type"]

    def get_response_json(self, query_params, **kwargs):
        """
        Get the response data from the API.

        Overrides the parent function to make multiple requests until
        we see "batchcomplete", rather than a single request to the
        endpoint. This ensures that global usage data used for calculating
        popularity is tabulated correctly.

        This also dynamically adjust the query parameters based on the response sizes
        for a given continue token. For more information see the DAG description.
        """
        batch_json = None
        gaicontinue = None
        iteration_count = 0

        for _ in range(self.mean_global_usage_limit):
            response_json = super().get_response_json(
                query_params,
                timeout=120,
            )

            # Update continue token for the next request
            self.continue_token = response_json.pop("continue", {})
            query_params.update(self.continue_token)
            logger.info(f"Continue token for next iteration: {self.continue_token}")

            current_gaicontinue = self.continue_token.get("gaicontinue")
            logger.debug(f"{current_gaicontinue=}")
            if current_gaicontinue == gaicontinue:
                # gaicontinue token can be None if all available results fit within
                # the batch limit, so we don't need to make an exception if it's None
                iteration_count += 1
            else:
                # Reset the iteration count if the continue token has changed
                iteration_count = 0
                gaicontinue = current_gaicontinue

            if iteration_count >= self.max_page_iteration_before_give_up:
                logger.warning(
                    f"Hit iteration count limit for '{gaicontinue}', "
                    "re-attempting with a bare token"
                )
                self.adjust_parameters_for_next_iteration(gaicontinue)
                break

            # Merge this response into the batch
            batch_json = self.merge_response_jsons(batch_json, response_json)

            if "batchcomplete" in response_json:
                logger.info("Found batchcomplete")
                # Reset the search props for the next batch
                self.current_props = self.default_props.copy()
                break
        return batch_json

    def get_should_continue(self, response_json):
        # Should not continue if continue_token is Falsy
        return self.continue_token

    def get_batch_data(self, response_json):
        image_pages = self.get_media_pages(response_json)
        if image_pages is not None:
            return image_pages.values()
        return None

    @staticmethod
    def get_media_pages(response_json):
        if response_json is not None:
            image_pages = response_json.get("query", {}).get("pages")
            if image_pages is not None:
                logger.info(f"Got {len(image_pages)} pages")
                return image_pages

        logger.warning(f"No pages in the image batch: {response_json}")
        return None

    def get_record_data(self, record):
        if not (foreign_identifier := record.get("pageid")):
            return None

        media_info = self.extract_media_info_dict(record)

        if not (valid_media_type := self.extract_media_type(media_info)):
            # Do not process unsupported media types, like Video
            return None

        if not (license_info := self.extract_license_info(media_info)):
            return None

        if not (url := media_info.get("url")):
            return None

        if not (foreign_landing_url := media_info.get("descriptionshorturl")):
            return None

        creator, creator_url = self.extract_creator_info(media_info)
        title = self.extract_title(media_info)
        filesize = media_info.get("size", 0)  # in bytes
        filetype = self.extract_file_type(media_info)
        meta_data = self.create_meta_data_dict(record)

        record_data = {
            "url": url,
            "foreign_landing_url": foreign_landing_url,
            "foreign_identifier": foreign_identifier,
            "license_info": license_info,
            "creator": creator,
            "creator_url": creator_url,
            "title": title,
            "filetype": filetype,
            "filesize": filesize,
            "meta_data": meta_data,
            "media_type": valid_media_type,
        }

        # Extend record_data with media-type specific fields
        funcs = {
            IMAGE: self.get_image_record_data,
            AUDIO: self.get_audio_record_data,
        }
        return funcs[valid_media_type](record_data, media_info)

    @staticmethod
    def get_image_record_data(record_data, media_info):
        """Extend record_data with image-specific fields."""
        if record_data["filetype"] == "svg":
            record_data["category"] = "illustration"

        return {
            **record_data,
            "width": media_info.get("width"),
            "height": media_info.get("height"),
        }

    def get_audio_record_data(self, record_data, media_info):
        """Extend record_data with audio-specific fields."""
        duration = int(float(media_info.get("duration", 0)) * 1000)
        record_data["duration"] = duration
        record_data["category"] = self.extract_audio_category(record_data)

        file_metadata = self.parse_audio_file_meta_data(media_info)
        if sample_rate := self.get_value_by_names(
            file_metadata, ["audio_sample_rate", "sample_rate"]
        ):
            record_data["sample_rate"] = sample_rate
        if bit_rate := self.get_value_by_names(
            file_metadata, ["bitrate_nominal", "bitrate"]
        ):
            record_data["bit_rate"] = bit_rate if bit_rate <= 2147483647 else None
        if channels := self.get_value_by_names(
            file_metadata, ["audio_channels", "channels"]
        ):
            record_data["meta_data"]["channels"] = channels

        return record_data

    def parse_audio_file_meta_data(self, media_info):
        """Parse out audio file metadata."""
        metadata = media_info.get("metadata", [])

        streams = self.get_value_by_name(metadata, "streams")
        if not streams:
            audio = self.get_value_by_name(metadata, "audio")
            streams = self.get_value_by_name(audio, "streams")

        if streams:
            streams_data = streams[0].get("value", [])
            file_data = self.get_value_by_name(streams_data, "header")
            # Fall back to streams_data
            return file_data or streams_data

        return []

    def adjust_parameters_for_next_iteration(self, gaicontinue: str | None) -> None:
        """
        Adjust the parameters for the next iteration. This removes properties based
        on what continue token is being iterated over, using heuristics determined by
        observation from the values that caused the overage.
        """
        if "gucontinue" in self.continue_token:
            # Exclude global usage info (i.e. popularity) from the query
            self.current_props["prop"] = self.ReturnProps.query_no_popularity
        if "iicontinue" in self.continue_token:
            # Exclude metadata from the query
            self.current_props["iiprop"] = self.ReturnProps.media_no_metadata

        # In order to appropriately adjust the continue token, we need to preserve the
        # primary iterator (if there is one) and reset the secondary iterator.
        current_continue = self.continue_token.get("continue", "||")
        reset_continue = current_continue.split("||")[0]

        self.continue_token = {
            "gaicontinue": gaicontinue,
            "continue": f"{reset_continue}||",
        }

    @staticmethod
    def extract_media_info_dict(media_data) -> dict:
        media_info_list = media_data.get("imageinfo")
        if media_info_list and isinstance(media_info_list, list):
            return media_info_list[0]
        return {}

    @staticmethod
    def get_value_by_name(key_value_list: list | None, prop_name: str):
        """Get the first value for the given prop_name in a list of key value pairs."""
        if key_value_list is None:
            key_value_list = []

        prop_list = [
            key_value_pair
            for key_value_pair in key_value_list
            if key_value_pair["name"] == prop_name
        ]
        if prop_list:
            return prop_list[0].get("value")

    @staticmethod
    def get_value_by_names(key_value_list: list, prop_names: list):
        """Get the first available value for one of the `prop_names` property names."""
        for prop_name in prop_names:
            if val := WikimediaCommonsDataIngester.get_value_by_name(
                key_value_list, prop_name
            ):
                return val

    @staticmethod
    def extract_media_type(media_info):
        media_type = media_info.get("mediatype")
        image_mediatypes = WikimediaCommonsDataIngester.image_mediatypes
        audio_mediatypes = WikimediaCommonsDataIngester.audio_mediatypes

        if media_type in image_mediatypes:
            return IMAGE
        elif media_type in audio_mediatypes:
            return AUDIO

        logger.info(
            f"Ignoring mediatype: {media_type} not in "
            f"valid mediatypes ({image_mediatypes}, {audio_mediatypes})"
        )
        return None

    @staticmethod
    def extract_audio_category(parsed_data):
        """
        Determine the audio category.

        Sets category to "pronunciation" for any audio with pronunciation
        of a word or a phrase.
        """
        for category in parsed_data["meta_data"].get("categories", []):
            if "pronunciation" in category.lower():
                return "pronunciation"

    @staticmethod
    def extract_ext_value(media_info: dict, ext_key: str) -> str | None:
        return media_info.get("extmetadata", {}).get(ext_key, {}).get("value")

    @staticmethod
    def extract_title(media_info):
        # Titles often have 'File:filename.jpg' form
        # We remove the 'File:' and extension from title
        title = WikimediaCommonsDataIngester.extract_ext_value(media_info, "ObjectName")
        if not title:
            title = media_info.get("title")
        if title.startswith("File:"):
            title = title.replace("File:", "", 1)
        last_dot_position = title.rfind(".")
        if last_dot_position > 0:
            possible_extension = title[last_dot_position:]
            if possible_extension.lower() in {".png", ".jpg", ".jpeg", ".ogg", ".wav"}:
                title = title[:last_dot_position]
        return title

    @staticmethod
    def extract_date_info(media_info):
        date_originally_created = WikimediaCommonsDataIngester.extract_ext_value(
            media_info, "DateTimeOriginal"
        )
        last_modified_at_source = WikimediaCommonsDataIngester.extract_ext_value(
            media_info, "DateTime"
        )
        return date_originally_created, last_modified_at_source

    @staticmethod
    def extract_creator_info(media_info):
        artist_string = WikimediaCommonsDataIngester.extract_ext_value(
            media_info, "Artist"
        )

        if not artist_string:
            return None, None

        artist_elem = html.fromstring(artist_string)
        # We take all text to replicate what is shown on Wikimedia Commons
        artist_text = "".join(artist_elem.xpath("//text()")).strip()
        url_list = list(artist_elem.iterlinks())
        artist_url = url_list[0][2] if url_list else None
        return artist_text, artist_url

    @staticmethod
    def extract_category_info(media_info):
        categories_string = (
            WikimediaCommonsDataIngester.extract_ext_value(media_info, "Categories")
            or ""
        )

        categories_list = categories_string.split("|")
        return categories_list

    @staticmethod
    def extract_file_type(media_info):
        filetype = media_info.get("url", "").split(".")[-1]
        return None if filetype == "" else filetype

    @staticmethod
    def extract_license_info(media_info) -> LicenseInfo | None:
        license_url = (
            WikimediaCommonsDataIngester.extract_ext_value(media_info, "LicenseUrl")
            or ""
        )
        # TODO Add public domain items
        # if license_url == "":
        #     license_name = extract_ext_value(media_info, "LicenseShortName") or ""
        #     if license_name.lower() in {"public_domain", "pdm-owner"}:
        #         pass

        return get_license_info(license_url=license_url.strip())

    @staticmethod
    def extract_geo_data(media_data):
        geo_properties = {
            "latitude": "GPSLatitude",
            "longitude": "GPSLongitude",
            "map_datum": "GPSMapDatum",
        }
        geo_data = {}
        for key, value in geo_properties.items():
            key_value = media_data.get(value, {}).get("value")
            if key_value:
                geo_data[key] = key_value
        return geo_data

    def extract_global_usage(self, media_data) -> int:
        """
        Extract the global usage count from the media data.
        The global usage count serves as a proxy for popularity data, since it
        represents how many pages across all available wikis a media item is used on.
        This uses a cache to record previous values for a given foreign ID, because
        it is possible that we might encounter a media item several times based on the
        querying method used (see "props" above). Not all results will have the same
        (if any) usage data, so we want to record and cache the highest value. Most
        items have no global usage data, so we only cache items that have a value.
        """
        global_usage_count = len(media_data.get("globalusage", []))
        foreign_id = media_data["pageid"]
        cached_usage_count = self.popularity_cache.get(foreign_id, 0)
        max_usage_count = max(global_usage_count, cached_usage_count)
        # Only cache if it's greater than zero, otherwise it'll just take up space
        if max_usage_count > 0:
            self.popularity_cache[foreign_id] = max_usage_count
        return max_usage_count

    def create_meta_data_dict(self, media_data):
        media_info = self.extract_media_info_dict(media_data)
        date_originally_created, last_modified_at_source = self.extract_date_info(
            media_info
        )
        categories_list = self.extract_category_info(media_info)
        description = self.extract_ext_value(media_info, "ImageDescription")
        meta_data = {
            "global_usage_count": self.extract_global_usage(media_data),
            "date_originally_created": date_originally_created,
            "last_modified_at_source": last_modified_at_source,
            "categories": categories_list,
            **self.extract_geo_data(media_data),
        }
        if description:
            description_text = " ".join(
                html.fromstring(description).xpath("//text()")
            ).strip()
            meta_data["description"] = description_text
        return meta_data

    def merge_response_jsons(self, left_json, right_json):
        # Note that we will keep the continue value from the right json in
        # the merged output!  This is because we assume the right json is
        # the later one in the sequence of responses.
        if left_json is None:
            return right_json

        left_pages = self.get_media_pages(left_json)
        right_pages = self.get_media_pages(right_json)

        if (
            left_pages is None
            or right_pages is None
            or left_pages.keys() != right_pages.keys()
        ):
            logger.warning("Cannot merge responses with different pages!")
            merged_json = None
        else:
            merged_json = deepcopy(left_json)
            merged_json.update(right_json)
            merged_pages = self.get_media_pages(merged_json)
            merged_pages.update(
                {
                    k: self.merge_media_pages(left_pages[k], right_pages[k])
                    for k in left_pages
                }
            )

        return merged_json

    @staticmethod
    def merge_media_pages(left_page, right_page):
        merged_page = deepcopy(left_page)
        merged_globalusage = left_page.get("globalusage", []) + right_page.get(
            "globalusage", []
        )
        merged_page.update(right_page)
        merged_page["globalusage"] = merged_globalusage

        return merged_page

    @staticmethod
    def derive_timestamp_pair(date):
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        utc_date = date_obj.replace(tzinfo=timezone.utc)
        start_timestamp = str(int(utc_date.timestamp()))
        end_timestamp = str(int((utc_date + timedelta(days=1)).timestamp()))
        logger.info(
            f"Start timestamp: {start_timestamp}, end timestamp: {end_timestamp}"
        )
        return start_timestamp, end_timestamp


def main(date):
    logger.info(f"Begin: Wikimedia Commons data ingestion for {date}")
    ingester = WikimediaCommonsDataIngester(date=date)
    ingester.ingest_records()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Wikimedia Commons API Job",
        add_help=True,
    )
    parser.add_argument(
        "--date", help="Identify media uploaded on a date (format: YYYY-MM-DD)."
    )
    args = parser.parse_args()
    if args.date:
        date = args.date
    else:
        date_obj = datetime.now() - timedelta(days=2)
        date = datetime.strftime(date_obj, "%Y-%m-%d")

    main(date)
