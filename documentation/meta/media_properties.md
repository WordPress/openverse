# Media Properties

_This document is auto-generated from the source code in
[/catalog/utilities/media_props_gen/generate_media_properties.py](https://github.com/WordPress/openverse/blob/main/catalog/utilities/media_props_gen/generate_media_properties.py)._

This is a list of the media properties, with the descriptions of corresponding
database columns and Python objects that are used to store and retrieve media
data. The order of the properties corresponds to their order in the `image_view`
materialized view. Property names typically match those of the database columns,
except when noted otherwise in the Python column's name property.

## Image Properties

| Name                                                  | DB Field                               | Python Column                                                                                                                                                                                           |
| ----------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`identifier`](#identifier)                           | uuid, nullable                         | [UUIDColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L500-L517) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                      |
| [`created_on`](#created_on)                           | timestamp with time zone, non-nullable | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`nullable=False, required=True, upsert_strategy=no_change`)                       |
| [`updated_on`](#updated_on)                           | timestamp with time zone, non-nullable | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                 |
| [`ingestion_type`](#ingestion_type)                   | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`provider`](#provider)                               | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`source`](#source)                                   | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`foreign_identifier`](#foreign_identifier)           | character varying (3000), nullable     | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                    |
| [`foreign_landing_url`](#foreign_landing_url)         | character varying (1000), nullable     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`nullable=True, required=True, upsert_strategy=newest_non_null`)                        |
| [`url`](#url)                                         | character varying (3000), non-nullable | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                       |
| [`thumbnail`](#thumbnail)                             | character varying (3000), nullable     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`name="thumbnail_url", nullable=True, required=False, upsert_strategy=newest_non_null`) |
| [`width`](#width)                                     | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                   |
| [`height`](#height)                                   | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                   |
| [`filesize`](#filesize)                               | integer, nullable                      | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                   |
| [`license`](#license)                                 | character varying (50), non-nullable   | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`name="license_", nullable=False, required=True, upsert_strategy=newest_non_null`)   |
| [`license_version`](#license_version)                 | character varying (25), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                    |
| [`creator`](#creator)                                 | character varying (2000), nullable     | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`creator_url`](#creator_url)                         | character varying (2000), nullable     | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                       |
| [`title`](#title)                                     | character varying (5000), nullable     | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`meta_data`](#meta_data)                             | jsonb, nullable                        | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                      |
| [`tags`](#tags)                                       | jsonb, nullable                        | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`nullable=True, required=False, upsert_strategy=merge_jsonb_arrays`)                   |
| [`watermarked`](#watermarked)                         | boolean, nullable                      | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                   |
| [`last_synced_with_source`](#last_synced_with_source) | timestamp with time zone, nullable     | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                 |
| [`removed_from_source`](#removed_from_source)         | boolean, non-nullable                  | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`nullable=False, required=True, upsert_strategy=false`)                             |
| [`filetype`](#filetype)                               | character varying (5), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`category`](#category)                               | character varying (80), nullable       | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                    |
| [`standardized_popularity`](#standardized_popularity) | double precision, nullable             | [CalculatedColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L259-L337) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                |

## Audio Properties

| Name                                                            | DB Field                                  | Python Column                                                                                                                                                                                                 |
| --------------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`identifier`](#identifier)                                     | uuid, nullable                            | [UUIDColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L500-L517) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                            |
| [`created_on`](#created_on)                                     | timestamp with time zone, non-nullable    | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`nullable=False, required=True, upsert_strategy=no_change`)                             |
| [`updated_on`](#updated_on)                                     | timestamp with time zone, non-nullable    | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                       |
| [`ingestion_type`](#ingestion_type)                             | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`provider`](#provider)                                         | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`source`](#source)                                             | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`foreign_identifier`](#foreign_identifier)                     | character varying (3000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                          |
| [`foreign_landing_url`](#foreign_landing_url)                   | character varying (1000), nullable        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`nullable=True, required=True, upsert_strategy=newest_non_null`)                              |
| [`url`](#url)                                                   | character varying (3000), non-nullable    | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                             |
| [`thumbnail`](#thumbnail)                                       | character varying (3000), nullable        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`name="thumbnail_url", nullable=True, required=False, upsert_strategy=newest_non_null`)       |
| [`filetype`](#filetype)                                         | character varying (5), nullable           | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`duration`](#duration)                                         | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                         |
| [`bit_rate`](#bit_rate)                                         | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                         |
| [`sample_rate`](#sample_rate)                                   | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                         |
| [`category`](#category)                                         | character varying (80), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`genres`](#genres)                                             | array of character varying (80), nullable | [ArrayColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L599-L651) (`nullable=True, required=False, upsert_strategy=newest_non_null, base_column=StringColumn`) |
| [`audio_set`](#audio_set)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                            |
| [`set_position`](#set_position)                                 | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                         |
| [`alt_files`](#alt_files)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`nullable=True, required=False, upsert_strategy=merge_jsonb_arrays`)                         |
| [`filesize`](#filesize)                                         | integer, nullable                         | [IntegerColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L216-L256) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                         |
| [`license`](#license)                                           | character varying (50), non-nullable      | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`name="license_", nullable=False, required=True, upsert_strategy=newest_non_null`)         |
| [`license_version`](#license_version)                           | character varying (25), nullable          | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=False, required=True, upsert_strategy=newest_non_null`)                          |
| [`creator`](#creator)                                           | character varying (2000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`creator_url`](#creator_url)                                   | character varying (2000), nullable        | [URLColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L550-L596) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                             |
| [`title`](#title)                                               | character varying (5000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |
| [`meta_data`](#meta_data)                                       | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                            |
| [`tags`](#tags)                                                 | jsonb, nullable                           | [JSONColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L388-L454) (`nullable=True, required=False, upsert_strategy=merge_jsonb_arrays`)                         |
| [`watermarked`](#watermarked)                                   | boolean, nullable                         | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                         |
| [`last_synced_with_source`](#last_synced_with_source)           | timestamp with time zone, nullable        | [TimestampColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L520-L547) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                       |
| [`removed_from_source`](#removed_from_source)                   | boolean, non-nullable                     | [BooleanColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L340-L385) (`nullable=False, required=True, upsert_strategy=false`)                                   |
| [`standardized_popularity`](#standardized_popularity)           | double precision, nullable                | [CalculatedColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L259-L337) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                      |
| [`audio_set_foreign_identifier`](#audio_set_foreign_identifier) | character varying (1000), nullable        | [StringColumn](https://github.com/WordPress/openverse/blob/main/catalog/dags/common/storage/columns.py#L457-L497) (`nullable=True, required=False, upsert_strategy=newest_non_null`)                          |

## Media Property Descriptions

### identifier

_Media Types_: `audio`, `image`

#### Description

The unique UUID identifier for the media item.

#### Object Shape

UUID

#### Selection Criteria

Created when the item is inserted into the main table.

#### Normalization and Validation

#### Existing Data Inconsistencies

### created_on

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### updated_on

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### ingestion_type

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### provider

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### source

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### foreign_identifier

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### foreign_landing_url

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### url

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### thumbnail

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### width

_Media Types_: `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### height

_Media Types_: `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### filesize

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### license

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### license_version

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### creator

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### creator_url

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### title

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### meta_data

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### tags

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### watermarked

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### last_synced_with_source

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### removed_from_source

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### filetype

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### category

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### standardized_popularity

_Media Types_: `audio`, `image`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### duration

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### bit_rate

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### sample_rate

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### genres

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### alt_files

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### audio_set

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### audio_set_foreign_identifier

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies

### set_position

_Media Types_: `audio`

#### Description

#### Object Shape

#### Selection Criteria

#### Normalization and Validation

#### Existing Data Inconsistencies
