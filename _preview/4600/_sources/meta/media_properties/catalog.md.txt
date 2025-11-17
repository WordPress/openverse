# Catalog Media Properties

_This document is auto-generated from the source code in
[/catalog/utilities/media_props_gen/generate_media_properties.py](https://github.com/WordPress/openverse/blob/main/catalog/utilities/media_props_gen/generate_media_properties.py)._

This is a list of the media properties, with the descriptions of corresponding
database columns and Python objects that are used to store and retrieve media
data. The order of the properties corresponds to their order in the `image`
table. Property names typically match those of the database columns, except when
noted otherwise in the Python column's name property.

## Image Properties

| Name                                                  | DB Field                               | Python Column                                                                                                                                                                                           |
| ----------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`identifier`](#identifier)                           | uuid, nullable                         | [UUIDColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L500-L517) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`created_on`](#created_on)                           | timestamp with time zone, non-nullable | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=no_change, nullable=False, required=True`)                       |
| [`updated_on`](#updated_on)                           | timestamp with time zone, non-nullable | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                 |
| [`ingestion_type`](#ingestion_type)                   | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`provider`](#provider)                               | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`source`](#source)                                   | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`foreign_identifier`](#foreign_identifier)           | text, nullable                         | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                    |
| [`foreign_landing_url`](#foreign_landing_url)         | text, nullable                         | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=True`)                        |
| [`url`](#url)                                         | text, non-nullable                     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                       |
| [`thumbnail`](#thumbnail)                             | text, nullable                         | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`name="thumbnail_url", upsert_strategy=newest_non_null, nullable=True, required=False`) |
| [`width`](#width)                                     | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`height`](#height)                                   | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`filesize`](#filesize)                               | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`license`](#license)                                 | character varying (50), non-nullable   | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`name="license_", upsert_strategy=newest_non_null, nullable=False, required=True`)   |
| [`license_version`](#license_version)                 | character varying (25), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                    |
| [`creator`](#creator)                                 | text, nullable                         | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`creator_url`](#creator_url)                         | text, nullable                         | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                       |
| [`title`](#title)                                     | text, nullable                         | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`meta_data`](#meta_data)                             | jsonb, nullable                        | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_objects, nullable=True, required=False`)                  |
| [`tags`](#tags)                                       | jsonb, nullable                        | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_arrays, nullable=True, required=False`)                   |
| [`watermarked`](#watermarked)                         | boolean, nullable                      | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`last_synced_with_source`](#last_synced_with_source) | timestamp with time zone, nullable     | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                 |
| [`removed_from_source`](#removed_from_source)         | boolean, non-nullable                  | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`upsert_strategy=false, nullable=False, required=True`)                             |
| [`filetype`](#filetype)                               | character varying (5), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`category`](#category)                               | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`standardized_popularity`](#standardized_popularity) | double precision, nullable             | [CalculatedColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L259-L337) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                |

## Audio Properties

| Name                                                            | DB Field                                  | Python Column                                                                                                                                                                                             |
| --------------------------------------------------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`identifier`](#identifier)                                     | uuid, nullable                            | [UUIDColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L500-L517) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                        |
| [`created_on`](#created_on)                                     | timestamp with time zone, non-nullable    | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=no_change, nullable=False, required=True`)                         |
| [`updated_on`](#updated_on)                                     | timestamp with time zone, non-nullable    | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                   |
| [`ingestion_type`](#ingestion_type)                             | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`provider`](#provider)                                         | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`source`](#source)                                             | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`foreign_identifier`](#foreign_identifier)                     | text, nullable                            | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                      |
| [`foreign_landing_url`](#foreign_landing_url)                   | text, nullable                            | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=True`)                          |
| [`url`](#url)                                                   | text, non-nullable                        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                         |
| [`thumbnail`](#thumbnail)                                       | text, nullable                            | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`name="thumbnail_url", upsert_strategy=newest_non_null, nullable=True, required=False`)   |
| [`filetype`](#filetype)                                         | character varying (5), nullable           | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`duration`](#duration)                                         | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`bit_rate`](#bit_rate)                                         | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`sample_rate`](#sample_rate)                                   | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`category`](#category)                                         | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`genres`](#genres)                                             | array of character varying (80), nullable | [ArrayColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L599-L651) (`upsert_strategy=merge_array, base_column=StringColumn, nullable=True, required=False`) |
| [`audio_set`](#audio_set)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_objects, nullable=True, required=False`)                    |
| [`set_position`](#set_position)                                 | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`alt_files`](#alt_files)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_arrays, nullable=True, required=False`)                     |
| [`filesize`](#filesize)                                         | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`license`](#license)                                           | character varying (50), non-nullable      | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`name="license_", upsert_strategy=newest_non_null, nullable=False, required=True`)     |
| [`license_version`](#license_version)                           | character varying (25), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                      |
| [`creator`](#creator)                                           | text, nullable                            | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`creator_url`](#creator_url)                                   | text, nullable                            | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                         |
| [`title`](#title)                                               | text, nullable                            | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`meta_data`](#meta_data)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_objects, nullable=True, required=False`)                    |
| [`tags`](#tags)                                                 | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_arrays, nullable=True, required=False`)                     |
| [`watermarked`](#watermarked)                                   | boolean, nullable                         | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`last_synced_with_source`](#last_synced_with_source)           | timestamp with time zone, nullable        | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`removed_from_source`](#removed_from_source)                   | boolean, non-nullable                     | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`upsert_strategy=false, nullable=False, required=True`)                               |
| [`standardized_popularity`](#standardized_popularity)           | double precision, nullable                | [CalculatedColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L259-L337) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                  |
| [`audio_set_foreign_identifier`](#audio_set_foreign_identifier) | text, nullable                            | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |

## Media Property Descriptions

### identifier

_Media Types_: `audio`, `image`

_DB Column Type_: `uuid, nullable`

#### Description

The unique UUID identifier for the media item. The `identifier` is generated
when the item is first inserted into the main table.

#### Object Shape

[UUID](https://www.postgresql.org/docs/current/datatype-uuid.html#DATATYPE-UUID)

----

### created_on

_Media Types_: `audio`, `image`

_DB Column Type_: `timestamp with time zone, non-nullable`

#### Description

The timestamp of when the media item was first added to Openverse catalog. This
timestamp is generated when the item is first inserted into the main table.

```{note}
This is _not_ the date when the item was first published on the source site.
```

----

### updated_on

_Media Types_: `audio`, `image`

_DB Column Type_: `timestamp with time zone, non-nullable`

#### Description

The timestamp of the last time any change was made to the media item. Unlike
`last_synced_with_source`, this can also be a change from a data cleaning step,
e.g. updating license URL in the `meta_data`, or fixing the URL using the
`batched_update` DAG.

----

### ingestion_type

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (80), nullable`

#### Description

The way the media item was ingested into the Openverse catalog.

- `common_crawl`: data extracted from the Common Crawl dataset, when the
  Creative Commons search API was first created.
- `provider_api` data is extracted from various CC media provider APIs.
- `sql_bulk_load` data is extracted from the SQL data dumps.

----

### provider

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (80), nullable`

#### Description

The name of the provider of the media metadata. This is usually, but not always,
the website that hosts the media item.

#### Object Shape

This is a keyword for the provider, a string in a "snake_case" form.

----

### source

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (80), nullable`

#### Description

The name of the source of the media item. It can be a collection on a provider
site, or the provider itself.

#### Object Shape

This is a keyword for the source, a string in a "snake_case" form.

----

### foreign_identifier

_Media Types_: `audio`, `image`

_DB Column Type_: `text, nullable`

#### Description

The unique identifier for the media item on the source site.

----

### foreign_landing_url

_Media Types_: `audio`, `image`

_DB Column Type_: `text, nullable`

#### Description

The URL of the landing page for the media item (not a direct link to the media
file). This should be unique for each media item. This value will be used on the
frontend as the URL to direct users to for downloading a media item from the
upstream provider.

----

### url

_Media Types_: `audio`, `image`

_DB Column Type_: `text, non-nullable`

#### Description

The direct URL to the media file, from which the media file can be downloaded.
This should be unique for each media item.

----

### thumbnail

_Media Types_: `audio`, `image`

_DB Column Type_: `text, nullable`

#### Description

The URL of a smaller, thumbnail, image for the media item.

#### Selection Criteria

The smallest acceptable size for a thumbnail is 600px at the longest edge. See
[comment in issue #675](https://github.com/WordPress/openverse/issues/675#issuecomment-1472399310).

----

### width

_Media Types_: `image`

_DB Column Type_: `integer, nullable`

#### Description

The width of the main image in pixels.

----

### height

_Media Types_: `image`

_DB Column Type_: `integer, nullable`

#### Description

The height of the main image in pixels.

#### Selection Criteria

If the provider does not provide the height and width of the image, it is
possible to send a head request to the direct url to extract this dat.

----

### filesize

_Media Types_: `audio`, `image`

_DB Column Type_: `integer, nullable`

#### Description

The size of the main media file in bytes. If not available in the API response,
it can be extracted from a head request response to the media file URL.

----

### license

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (50), non-nullable`

#### Description

The slug of the license under which the media item is licensed. For the list of
available license slugs, see
[openverse-attribution package](https://github.com/WordPress/openverse/tree/main/packages/python/openverse-attribution/src/openverse_attribution/license_name.py).

----

### license_version

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (25), nullable`

#### Description

The string representing the version of the license. PublicDomain has no version
which is denoted as "N/A".

----

### creator

_Media Types_: `audio`, `image`

_DB Column Type_: `text, nullable`

#### Description

The name of the creator of the media item. Some providers use "Unknown" or
similar for unknown creators, see
[issue #1326](https://github.com/WordPress/openverse/issues/1326).

----

### creator_url

_Media Types_: `audio`, `image`

_DB Column Type_: `text, nullable`

#### Description

The URL of the creator's page, usually on the source site.

----

### title

_Media Types_: `audio`, `image`

_DB Column Type_: `text, nullable`

#### Description

The title of the media item.

#### Existing Data Inconsistencies

Provider scripts may include html tags in record titles, see
[issue #1441](https://github.com/WordPress/openverse/issues/1441). Some
Wikimedia titles in the database still include "FILE:" prefix, and unnecessary
file extension, which is
[hot-fixed](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L50)
in the frontend. Some titles were [incorrectly encoded](#encoding-problems), for
which there is a
[hot-fix in the frontend](https://github.com/WordPress/openverse/blob/70d57a91318a5b368fc0f1a244847bc27becefbd/frontend/src/utils/decode-media-data.ts#L73).

----

### meta_data

_Media Types_: `audio`, `image`

_DB Column Type_: `jsonb, nullable`

#### Description

A JSONB object containing additional metadata about the media item. This must
contain the `license_url` (automatically added by the `MediaStore` class from
the `License` object).

#### Selection Criteria

Relevant information that is not covered by other fields should be added here.
This includes such items as the dates of creation, publication, geographical
data, descriptions, and popularity data.

----

### tags

_Media Types_: `audio`, `image`

_DB Column Type_: `jsonb, nullable`

#### Description

The list of tags associated with the media item.

#### Object Shape

A JSONB array of dictionaries:

```
{
"name": "tag1",
"provider": "wordpress",
"accuracy": 0.95}
```

`accuracy` field with a float value is only available for machine-generated
tags. If there are no tags, the field should be set to null, not an empty array
or empty object.

#### Normalization and Validation

Tags are cleaned in the `MediaStore` class. The tags that contain license slugs
are removed because they are often misleading, using a different license than
the media item itself. See
[cc-archive issue #253](https://github.com/cc-archive/cccatalog-api/issues/253).

#### Existing Data Inconsistencies

The cleanup process in data refresh fixes the following tag inconsistencies:

- Empty tags (`{}`) are filtered out, see
  [cc-archive issue #130](https://github.com/cc-archive/cccatalog-api/issues/130).
- Tags with license slugs, as well as some other deny-listed tags, are filtered
  out.
- Some machine-generated tags have accuracy lower than 90% and are unreliable.
  These tags are filtered out. Some inconsistencies are not fixed by the cleanup
  process:
- Incorrectly [encoded tags](#encoding-problems), see
  [issue #1927](https://github.com/WordPress/openverse/issues/1927). This can
  result in duplicate tags when the frontend decodes the tags.
- Tags with leading or trailing spaces, see
  [issue #4199](https://github.com/WordPress/openverse/issues/4199) Previously
  existing, but now fixed, inconsistencies: Identical duplicate tags were
  filtered out in [#1556](https://github.com/WordPress/openverse/issues/1566)

----

### watermarked

_Media Types_: `audio`, `image`

_DB Column Type_: `boolean, nullable`

#### Description

Whether the image has a discernible watermark. If this field is null or false,
it does not mean the image doesn't have a watermark. This field was set to true
for some CommonCrawl providers (McCord Museum, 500px, FloraOn, IHA). Currently,
no provider script or SQL ingestion sets this field value.

----

### last_synced_with_source

_Media Types_: `audio`, `image`

_DB Column Type_: `timestamp with time zone, nullable`

#### Description

For new items, the timestamp that is the same as the `created_on`. For items
that were updated during re-ingestion, the timestamp of re-ingestion.

----

### removed_from_source

_Media Types_: `audio`, `image`

_DB Column Type_: `boolean, non-nullable`

#### Description

Set to `True` for items that were not updated during re-run of the provider
script. Items that have `True` in `removed_from_source` are not added to the ES
index during the data refresh process.

#### Selection Criteria

[`expire_old_images`](https://github.com/WordPress/openverse/tree/main/catalog/dags/retired/common/loader/sql.py)
DAG added in
[Expiration of outdated images in the database](https://github.com/cc-archive/cccatalog/pull/483)
was used to set `removed_from_source` to `True` for images that were updated
more than `OLDEST_PER_PROVIDER` value.

----

### filetype

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (5), nullable`

#### Description

The filetype (extension) of the main media file (not the MIME type). If the
filetype is not available in the API response, it can be extracted from the URL
extension or from the HEAD response from the media direct URL.

#### Normalization and Validation

The
[`extract_filetype` function in `catalog/dags/common/extensions.py`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/extensions.py#L7C5-L7C21)
is used to get the file extension from a URL. The function returns the file
extension in lowercase. Equivalent image file types are normalized to a single
file type, see
[`FILETYPE_EQUIVALENTS`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/storage/media.py#L42).

----

### category

_Media Types_: `audio`, `image`

_DB Column Type_: `character varying (80), nullable`

#### Description

One of the media category Enum values:
[`ImageCategory`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/loader/provider_details.py#L137-L141)
and
[`AudioCategory`](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/loader/provider_details.py#L144-L151).

#### Selection Criteria

Category is assigned heuristically based on the extension and
[default categories per provider](https://github.com/WordPress/openverse/tree/main/catalog/dags/common/loader/provider_details.py#L155).

----

### standardized_popularity

_Media Types_: `audio`, `image`

_DB Column Type_: `double precision, nullable`

#### Description

Normalized popularity, a calculated column. Only available for providers that
have popularity data.

#### Normalization and Validation

The value is updated monthly during the data refresh process.

----

### duration

_Media Types_: `audio`

_DB Column Type_: `integer, nullable`

#### Description

The duration of the main audio file in milliseconds.

----

### bit_rate

_Media Types_: `audio`

_DB Column Type_: `integer, nullable`

#### Description

The bit rate of the main audio file.

----

### sample_rate

_Media Types_: `audio`

_DB Column Type_: `integer, nullable`

#### Description

The sample rate of the main audio file.

----

### genres

_Media Types_: `audio`

_DB Column Type_: `array of character varying (80), nullable`

#### Description

List of genres associated with the audio.

----

### alt_files

_Media Types_: `audio`

_DB Column Type_: `jsonb, nullable`

#### Description

The list of alternative file details for the audio (different formats/ quality).

#### Object Shape

JSONB array of dictionaries:

```
[
    {
        "url": "http://example.com/audio.mp3",
        "filesize": 123456,
        "bit_rate": 128,
        "sample_rate": 44100
    }
]
```

- `url` (string): the direct URL of the alternative file.
- `filesize` (integer): the size of the alternative file in bytes.
- `filetype` (string): the file type (extension) of the alternative file.
- `bit_rate` (integer): the bit rate of the alternative file.
- `sample_rate` (integer): the sample rate of the alternative file.
- `duration` (integer, optional): the duration of the alternative file in
  milliseconds.

----

### audio_set

_Media Types_: `audio`

_DB Column Type_: `jsonb, nullable`

#### Description

The information about the audio set (collection, album) that the audio belongs
to.

#### Object Shape

JSONB object:

```
{
    "title": "Audio Set Title",
    "foreign_landing_url": "http://example.com",
    "thumbnail": "http://example.com/thumbnail.jpg",
    "creator": "Creator Name",
    "creator_url": "http://example.com/creator",
    "foreign_identifier": "123456"
}
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

----

### audio_set_foreign_identifier

_Media Types_: `audio`

_DB Column Type_: `text, nullable`

#### Description

Unique identifier for the audio set on the source site.

----

### set_position

_Media Types_: `audio`

_DB Column Type_: `integer, nullable`

#### Description

The position of the audio in the audio set.

----

## Encoding problems

In the beginning of the project, some items were saved to the database with
encoding problems. There are 3 ways that non-ASCII symbols were incorrectly
saved:

- escaped with double backslashes instead of the single backslash, e.g. `ä` ->
  `\\u00e4`
- escaped without a backslash, e.g. `ä` -> `u00e4`
- x-escaped with double backslashes, e.g. `ä` -> `\\x61`

With subsequent data re-ingestions, most titles were fixed. This problem still
exists for titles of items that were not re-ingested, and for fields that are
not simply replaced during re-ingestion, such as `tags` and
`meta_data.description`. The frontend uses a hotfix to replace these encoding
problems with the correct characters in
[title](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L73),
[tags](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L86)
and
[creator](https://github.com/WordPress/openverse/tree/main/frontend/src/utils/decode-media-data.ts#L124).
