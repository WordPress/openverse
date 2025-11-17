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
| [`foreign_identifier`](#foreign_identifier)           | character varying (3000), nullable     | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                    |
| [`foreign_landing_url`](#foreign_landing_url)         | character varying (1000), nullable     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=True`)                        |
| [`url`](#url)                                         | character varying (3000), non-nullable | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                       |
| [`thumbnail`](#thumbnail)                             | character varying (3000), nullable     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`name="thumbnail_url", upsert_strategy=newest_non_null, nullable=True, required=False`) |
| [`width`](#width)                                     | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`height`](#height)                                   | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`filesize`](#filesize)                               | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`license`](#license)                                 | character varying (50), non-nullable   | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`name="license_", upsert_strategy=newest_non_null, nullable=False, required=True`)   |
| [`license_version`](#license_version)                 | character varying (25), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                    |
| [`creator`](#creator)                                 | character varying (2000), nullable     | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
| [`creator_url`](#creator_url)                         | character varying (2000), nullable     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                       |
| [`title`](#title)                                     | character varying (5000), nullable     | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                    |
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
| [`foreign_identifier`](#foreign_identifier)                     | character varying (3000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                      |
| [`foreign_landing_url`](#foreign_landing_url)                   | character varying (1000), nullable        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=True`)                          |
| [`url`](#url)                                                   | character varying (3000), non-nullable    | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=False, required=True`)                         |
| [`thumbnail`](#thumbnail)                                       | character varying (3000), nullable        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`name="thumbnail_url", upsert_strategy=newest_non_null, nullable=True, required=False`)   |
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
| [`creator`](#creator)                                           | character varying (2000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`creator_url`](#creator_url)                                   | character varying (2000), nullable        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                         |
| [`title`](#title)                                               | character varying (5000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |
| [`meta_data`](#meta_data)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_objects, nullable=True, required=False`)                    |
| [`tags`](#tags)                                                 | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`upsert_strategy=merge_jsonb_arrays, nullable=True, required=False`)                     |
| [`watermarked`](#watermarked)                                   | boolean, nullable                         | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                     |
| [`last_synced_with_source`](#last_synced_with_source)           | timestamp with time zone, nullable        | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                   |
| [`removed_from_source`](#removed_from_source)                   | boolean, non-nullable                     | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`upsert_strategy=false, nullable=False, required=True`)                               |
| [`standardized_popularity`](#standardized_popularity)           | double precision, nullable                | [CalculatedColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L259-L337) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                  |
| [`audio_set_foreign_identifier`](#audio_set_foreign_identifier) | character varying (1000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`upsert_strategy=newest_non_null, nullable=True, required=False`)                      |

## Media Property Descriptions

### identifier

_Media Types_: `audio`, `image`

#### Description

The unique UUID identifier for the media item.

#### Object Shape

UUID

#### Selection Criteria

Created when the item is inserted into the main table.

----

### created_on

_Media Types_: `audio`, `image`

----

### updated_on

_Media Types_: `audio`, `image`

----

### ingestion_type

_Media Types_: `audio`, `image`

----

### provider

_Media Types_: `audio`, `image`

----

### source

_Media Types_: `audio`, `image`

----

### foreign_identifier

_Media Types_: `audio`, `image`

----

### foreign_landing_url

_Media Types_: `audio`, `image`

----

### url

_Media Types_: `audio`, `image`

----

### thumbnail

_Media Types_: `audio`, `image`

----

### width

_Media Types_: `image`

----

### height

_Media Types_: `image`

----

### filesize

_Media Types_: `audio`, `image`

----

### license

_Media Types_: `audio`, `image`

----

### license_version

_Media Types_: `audio`, `image`

----

### creator

_Media Types_: `audio`, `image`

----

### creator_url

_Media Types_: `audio`, `image`

----

### title

_Media Types_: `audio`, `image`

----

### meta_data

_Media Types_: `audio`, `image`

----

### tags

_Media Types_: `audio`, `image`

----

### watermarked

_Media Types_: `audio`, `image`

----

### last_synced_with_source

_Media Types_: `audio`, `image`

----

### removed_from_source

_Media Types_: `audio`, `image`

----

### filetype

_Media Types_: `audio`, `image`

----

### category

_Media Types_: `audio`, `image`

----

### standardized_popularity

_Media Types_: `audio`, `image`

----

### duration

_Media Types_: `audio`

----

### bit_rate

_Media Types_: `audio`

----

### sample_rate

_Media Types_: `audio`

----

### genres

_Media Types_: `audio`

----

### alt_files

_Media Types_: `audio`

----

### audio_set

_Media Types_: `audio`

----

### audio_set_foreign_identifier

_Media Types_: `audio`

----

### set_position

_Media Types_: `audio`
