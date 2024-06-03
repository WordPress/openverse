# identifier

## Description

The unique UUID identifier for the media item. The `identifier` is generated
when the item is first inserted into the main table.

## Object Shape

[UUID](https://www.postgresql.org/docs/current/datatype-uuid.html#DATATYPE-UUID)

# created_on

## Description

The timestamp of when the media item was first added to Openverse catalog. This
timestamp is generated when the item is first inserted into the main table.

```{note}
This is _not_ the date when the item was first published on the source site.
```

# updated_on

## Description

The timestamp of the last time any change was made to the media item. Unlike
`last_synced_with_source`, this can also be a change from a data cleaning step,
e.g. updating license URL in the `meta_data`, or fixing the URL using the
`batched_update` DAG.

# ingestion_type

## Description

The way the media item was ingested into the Openverse catalog.

- `common_crawl`: data extracted from the Common Crawl dataset, when the
  Creative Commons search API was first created.
- `provider_api` data is extracted from various CC media provider APIs.
- `sql_bulk_load` data is extracted from the SQL data dumps.

# provider

## Description

The name of the provider of the media metadata. This is usually, but not always,
the website that hosts the media item.

## Object Shape

This is a keyword for the provider, a string in a "snake_case" form.

# source

## Description

The name of the source of the media item. It can be a collection on a provider
site, or the provider itself.

## Object Shape

This is a keyword for the source, a string in a "snake_case" form.

# foreign_identifier

## Description

The unique identifier for the media item on the source site.

# foreign_landing_url

## Description

The URL of the landing page for the media item (not a direct link to the media
file). This should be unique for each media item. This value will be used on the
frontend as the URL to direct users to for downloading a media item from the
upstream provider.

# url

## Description

The direct URL to the media file, from which the media file can be downloaded.
This should be unique for each media item.

# thumbnail

## Description

The URL of a smaller, thumbnail, image for the media item.

## Selection Criteria

The smallest acceptable size for a thumbnail is 600px at the longest edge. See
[comment in issue #675](https://github.com/WordPress/openverse/issues/675#issuecomment-1472399310).

# width

## Description

The width of the main image in pixels.

# height

## Description

The height of the main image in pixels.

## Selection Criteria

If the provider does not provide the height and width of the image, it is
possible to send a head request to the direct url to extract this dat.

# filesize

## Description

The size of the main media file in bytes. If not available in the API response,
it can be extracted from a head request response to the media file URL.

# license

## Description

The slug of the license under which the media item is licensed. For the list of
available license slugs, see
[openverse-attribution package](https://github.com/WordPress/openverse/tree/main/packages/python/openverse-attribution/src/openverse_attribution/license_name.py).

# license_version

## Description

The string representing the version of the license. PublicDomain has no version
which is denoted as "N/A".

# creator

## Description

The name of the creator of the media item. Some providers use "Unknown" or
similar for unknown creators, see
[issue #1326](https://github.com/WordPress/openverse/issues/1326).

# creator_url

## Description

The URL of the creator's page, usually on the source site.

# title

## Description

The title of the media item.

## Existing Data Inconsistencies

Provider scripts may include html tags in record titles, see
[issue #1441](https://github.com/WordPress/openverse/issues/1441).

Some Wikimedia titles in the database still include "FILE:" prefix, and
unnecessary file extension, which is
[hot-fixed](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L50)
in the frontend. Some titles were incorrectly decoded, for which there is a
[hot-fix in the frontend](https://github.com/WordPress/openverse/blob/70d57a91318a5b368fc0f1a244847bc27becefbd/frontend/src/utils/decode-media-data.ts#L73).

# meta_data

## Description

A JSONB object containing additional metadata about the media item. This must
contain the `license_url` (automatically added by the `MediaStore` class from
the `License` object).

## Selection Criteria

Relevant information that is not covered by other fields should be added here.
This includes such items as the dates of creation, publication, geographical
data, descriptions, and popularity data.

# tags

## Description

The list of tags associated with the media item.

## Object Shape

A JSONB array of dictionaries: `{"name": "tag1", "provider": "wordpress"}`. Some
tags are machine-generated, and include an `accuracy` field with a float value.

If there are no tags, the field should be set to null, not an empty array or
empty object.

## Normalization and Validation

Tags are cleaned in the `MediaStore` class. The tags that contain license slugs
are removed because they are often misleading, using a different license than
the media item itself. See
[cc-archive issue #253](https://github.com/cc-archive/cccatalog-api/issues/253).

## Existing Data Inconsistencies

The cleanup process in data refresh fixes the following tag inconsistencies:

- Empty tags (`{}`) are filtered out, see
  [cc-archive issue #130](https://github.com/cc-archive/cccatalog-api/issues/130).
- Tags with license slugs, as well as some other deny-listed tags, are filtered
  out.
- Some machine-generated tags have accuracy lower than 90% and are unreliable.
  These tags are filtered out.

Some inconsistencies are not fixed by the cleanup process:

- Incorrectly encoded tags, see
  [issue #1927](https://github.com/WordPress/openverse/issues/1927). This can
  result in duplicate tags when the frontend decodes the tags.
- Tags with leading or trailing spaces, see
  [issue #4199](https://github.com/WordPress/openverse/issues/4199)

Previously existing, but now fixed, inconsistencies: Identical duplicate tags
were filtered out in [#1556](https://github.com/WordPress/openverse/issues/1566)

# watermarked

## Description

Whether the image has a discernible watermark. If this field is null or false,
it does not mean the image doesn't have a watermark. This field was set to true
for some CommonCrawl providers (McCord Museum, 500px, FloraOn, IHA). Currently,
no provider script or SQL ingestion sets this field value.

# last_synced_with_source

## Description

For new items, the timestamp that is the same as the `created_on`. For items
that were updated during re-ingestion, the timestamp of re-ingestion.

# removed_from_source

## Description

Set to `True` for items that were not updated during re-run of the provider
script. Items that have `True` in `removed_from_source` are not added to the ES
index during the data refresh process.

## Selection Criteria

[`expire_old_images`](https://github.com/WordPress/openverse/tree/main/catalog/dags/retired/common/loader/sql.py)
DAG added in
[Expiration of outdated images in the database](https://github.com/cc-archive/cccatalog/pull/483)
was used to set `removed_from_source` to `True` for images that were updated
more than `OLDEST_PER_PROVIDER` value.

# filetype

## Description

The filetype (extension) of the main media file (not the MIME type). If the
filetype is not available in the API response, it can be extracted from the URL
extension or from the HEAD response from the media direct URL.

## Normalization and Validation

The
[`extract_filetype` function in `catalog/dags/common/extensions.py`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/extensions.py#L7C5-L7C21)
is used to get the file extension from a URL. The function returns the file
extension in lowercase. Equivalent image file types are normalized to a single
file type, see
[`FILETYPE_EQUIVALENTS`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/storage/media.py#L42).

# category

## Description

One of the media category Enum values:
[`ImageCategory`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/loader/provider_details.py#L137-L141)
and
[`AudioCategory`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/loader/provider_details.py#L144-L151).

## Selection Criteria

Category is assigned heuristically based on the extension and
[default categories per provider](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/loader/provider_details.py#L155).

# standardized_popularity

## Description

Normalized popularity, a calculated column. Only available for providers that
have popularity data.

## Normalization and Validation

The value is updated monthly during the data refresh process.

# duration

## Description

The duration of the main audio file in milliseconds.

# bit_rate

## Description

The bit rate of the main audio file.

# sample_rate

## Description

The sample rate of the main audio file.

# genres

## Description

List of genres associated with the audio.

# alt_files

## Description

The list of alternative file details for the audio (different formats/ quality).

## Object Shape

JSONB array of dictionaries:

```
[{"url": "http://example.com/audio.mp3", "filesize": 123456, "bit_rate": 128, "sample_rate": 44100}]
```

- `url` (string): the direct URL of the alternative file.
- `filesize` (integer): the size of the alternative file in bytes.
- `filetype` (string): the file type (extension) of the alternative file.
- `bit_rate` (integer): the bit rate of the alternative file.
- `sample_rate` (integer): the sample rate of the alternative file.
- `duration` (integer, optional): the duration of the alternative file in
  milliseconds.

# audio_set

## Description

The information about the audio set (collection, album) that the audio belongs
to.

## Object Shape

JSONB object:

```
{"title": "Audio Set Title", "foreign_landing_url": "http://example.com", "thumbnail": "http://example.com/thumbnail.jpg", "creator": "Creator Name", "creator_url": "http://example.com/creator", "foreign_identifier": "123456"}
```

- `title` (string): the title of the audio set.
- `foreign_landing_url` (string): the URL of the audio set on the source site.
- `thumbnail` (string): the URL of the thumbnail image for the audio set.
- `creator` (string): the name of the creator of the audio set.
- `creator_url` (string): the URL of the creator's page, usually on the source
  site.
- `foreign_identifier` (string): the unique identifier for the audio set on the
  source site. This identifier is saved in the `audio_set_foreign_identifier`
  field of the TSV and catalog audio table.

# audio_set_foreign_identifier

## Description

Unique identifier for the audio set on the source site.

# set_position

## Description

The position of the audio in the audio set.
