# API Media Properties

_This document is auto-generated from the source code in
[/api/api/management/commands/documentmedia.py](https://github.com/WordPress/openverse/blob/main/api/api/management/commands/documentmedia.py)._

This is a list of the media properties, with the descriptions of corresponding
database columns and Python objects that are used to store and retrieve media
data.

## General notes

The columns are sorted alphabetically and separated into relations (used to
establish relationships to other models) and values (used to hold some data
value). Note that relation fields are always nullable.

## Audio

### Relations

| Name                                | Type                                                                                          | DB type | Nature       | To               |
| ----------------------------------- | --------------------------------------------------------------------------------------------- | ------- | ------------ | ---------------- |
| `audio_report`                      | [`ForeignKey`](https://docs.djangoproject.com/en/dev/ref/models/fields/#foreignkey)           | `uuid`  | One To Many  | `AudioReport`    |
| `audiodecision`                     | [`ManyToManyField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#manytomanyfield) |         | Many To Many | `AudioDecision`  |
| [`audioset`](#Audio-audioset-notes) | `ForeignObject`                                                                               |         | Many To One  | `AudioSet`       |
| `deleted_audio`                     | [`OneToOneField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `DeletedAudio`   |
| `lists`                             | [`ManyToManyField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#manytomanyfield) |         | Many To Many | `AudioList`      |
| `sensitive_audio`                   | [`OneToOneField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `SensitiveAudio` |

### Values

| Name                                                                        | Type                                                                                                                                                                               | DB type                    | Constraints                   | Default |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ----------------------------- | ------- |
| [`alt_files`](#Audio-alt_files-notes)                                       | [`JSONField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield)                                                                                                  | `jsonb`                    |                               |         |
| [`audio_set_foreign_identifier`](#Audio-audio_set_foreign_identifier-notes) | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(1000)`            |                               |         |
| [`audio_set_position`](#Audio-audio_set_position-notes)                     | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)                                                                                            | `integer`                  |                               |         |
| [`bit_rate`](#Audio-bit_rate-notes)                                         | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)                                                                                            | `integer`                  |                               |         |
| [`category`](#Audio-category-notes)                                         | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(80)`              |                               |         |
| `created_on`                                                                | [`DateTimeField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield)                                                                                          | `timestamp with time zone` | not null                      |         |
| [`creator`](#Audio-creator-notes)                                           | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(2000)`            |                               |         |
| [`creator_url`](#Audio-creator_url-notes)                                   | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(2000)`            |                               |         |
| [`duration`](#Audio-duration-notes)                                         | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)                                                                                            | `integer`                  |                               |         |
| [`filesize`](#Audio-filesize-notes)                                         | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)                                                                                            | `integer`                  |                               |         |
| [`filetype`](#Audio-filetype-notes)                                         | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(80)`              |                               |         |
| [`foreign_identifier`](#Audio-foreign_identifier-notes)                     | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(1000)`            |                               |         |
| [`foreign_landing_url`](#Audio-foreign_landing_url-notes)                   | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(1000)`            |                               |         |
| [`genres`](#Audio-genres-notes)                                             | [`ArrayField`](https://docs.djangoproject.com/en/dev/ref/contrib/postgres/fields/#arrayfield) of [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield) | `varchar(80)[]`            | not blank                     |         |
| [`id`](#Audio-id-notes)                                                     | [`AutoField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#autofield)                                                                                                  | `integer`                  | not null; unique; primary key |         |
| [`identifier`](#Audio-identifier-notes)                                     | [`UUIDField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#uuidfield)                                                                                                  | `uuid`                     | not null; not blank; unique   |         |
| `last_synced_with_source`                                                   | [`DateTimeField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield)                                                                                          | `timestamp with time zone` |                               |         |
| [`license`](#Audio-license-notes)                                           | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(50)`              | not null; not blank           |         |
| [`license_version`](#Audio-license_version-notes)                           | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(25)`              |                               |         |
| `meta_data`                                                                 | [`JSONField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield)                                                                                                  | `jsonb`                    |                               |         |
| [`provider`](#Audio-provider-notes)                                         | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(80)`              |                               |         |
| `removed_from_source`                                                       | [`BooleanField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#booleanfield)                                                                                            | `boolean`                  | not null; not blank           | `False` |
| [`sample_rate`](#Audio-sample_rate-notes)                                   | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)                                                                                            | `integer`                  |                               |         |
| [`source`](#Audio-source-notes)                                             | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(80)`              |                               |         |
| [`tags`](#Audio-tags-notes)                                                 | [`JSONField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield)                                                                                                  | `jsonb`                    |                               |         |
| [`thumbnail`](#Audio-thumbnail-notes)                                       | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(1000)`            |                               |         |
| [`title`](#Audio-title-notes)                                               | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(2000)`            |                               |         |
| `updated_on`                                                                | [`DateTimeField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield)                                                                                          | `timestamp with time zone` | not null                      |         |
| [`url`](#Audio-url-notes)                                                   | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)                                                                                                  | `varchar(1000)`            | unique                        |         |
| `view_count`                                                                | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)                                                                                            | `integer`                  |                               | `0`     |
| `watermarked`                                                               | [`BooleanField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#booleanfield)                                                                                            | `boolean`                  |                               |         |

### Notes

(Audio-alt_files-notes)=

#### `alt_files`

**Help text:** JSON describing alternative files for this audio.

(Audio-audio_set_foreign_identifier-notes)=

#### `audio_set_foreign_identifier`

**Help text:** Reference to set of which this track is a part.

(Audio-audio_set_position-notes)=

#### `audio_set_position`

**Help text:** Ordering of the audio in the set.

(Audio-audioset-notes)=

#### `audioset`

This is a virtual foreign-key to `AudioSet` built on top of the fields
`audio_set_foreign_identifier` and `provider`.

(Audio-bit_rate-notes)=

#### `bit_rate`

**Help text:** Number in bits per second, eg. 128000.

(Audio-category-notes)=

#### `category`

**Help text:** The top-level classification of this media file.

(Audio-creator-notes)=

#### `creator`

**Help text:** The name of the media creator.

(Audio-creator_url-notes)=

#### `creator_url`

**Help text:** A direct link to the media creator.

(Audio-duration-notes)=

#### `duration`

**Help text:** The time length of the audio file in milliseconds.

(Audio-filesize-notes)=

#### `filesize`

**Help text:** Number in bytes, e.g. 1024.

(Audio-filetype-notes)=

#### `filetype`

**Help text:** The type of the file, related to the file extension.

(Audio-foreign_identifier-notes)=

#### `foreign_identifier`

**Help text:** The identifier provided by the upstream source.

(Audio-foreign_landing_url-notes)=

#### `foreign_landing_url`

**Help text:** The landing page of the work.

(Audio-genres-notes)=

#### `genres`

**Help text:** An array of audio genres such as `rock`, `electronic` for `music`
category, or `politics`, `sport`, `education` for `podcast` category

(Audio-id-notes)=

#### `id`

This is Django's automatic primary key, used for models that do not define one
explicitly.

(Audio-identifier-notes)=

#### `identifier`

**Help text:** Our unique identifier for an open-licensed work.

(Audio-license-notes)=

#### `license`

**Help text:** The name of license for the media.

(Audio-license_version-notes)=

#### `license_version`

**Help text:** The version of the media license.

(Audio-provider-notes)=

#### `provider`

**Help text:** The content provider, e.g. Flickr, Jamendo...

(Audio-sample_rate-notes)=

#### `sample_rate`

**Help text:** Number in hertz, eg. 44100.

(Audio-source-notes)=

#### `source`

**Help text:** The source of the data, meaning a particular dataset. Source and
provider can be different. Eg: the Google Open Images dataset is
source=openimages, but provider=flickr.

(Audio-tags-notes)=

#### `tags`

**Help text:** Tags with detailed metadata, such as accuracy.

(Audio-thumbnail-notes)=

#### `thumbnail`

**Help text:** The thumbnail for the media.

(Audio-title-notes)=

#### `title`

**Help text:** The name of the media.

(Audio-url-notes)=

#### `url`

**Help text:** The actual URL to the media file.

## Image

### Relations

| Name              | Type                                                                                          | DB type | Nature       | To               |
| ----------------- | --------------------------------------------------------------------------------------------- | ------- | ------------ | ---------------- |
| `deleted_image`   | [`OneToOneField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `DeletedImage`   |
| `image_report`    | [`ForeignKey`](https://docs.djangoproject.com/en/dev/ref/models/fields/#foreignkey)           | `uuid`  | One To Many  | `ImageReport`    |
| `imagedecision`   | [`ManyToManyField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#manytomanyfield) |         | Many To Many | `ImageDecision`  |
| `lists`           | [`ManyToManyField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#manytomanyfield) |         | Many To Many | `ImageList`      |
| `sensitive_image` | [`OneToOneField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `SensitiveImage` |

### Values

| Name                                                      | Type                                                                                      | DB type                    | Constraints                   | Default |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------- | ----------------------------- | ------- |
| [`category`](#Image-category-notes)                       | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| `created_on`                                              | [`DateTimeField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield) | `timestamp with time zone` | not null                      |         |
| [`creator`](#Image-creator-notes)                         | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(2000)`            |                               |         |
| [`creator_url`](#Image-creator_url-notes)                 | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(2000)`            |                               |         |
| [`filesize`](#Image-filesize-notes)                       | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)   | `integer`                  |                               |         |
| [`filetype`](#Image-filetype-notes)                       | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| [`foreign_identifier`](#Image-foreign_identifier-notes)   | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(1000)`            |                               |         |
| [`foreign_landing_url`](#Image-foreign_landing_url-notes) | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(1000)`            |                               |         |
| [`height`](#Image-height-notes)                           | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)   | `integer`                  |                               |         |
| [`id`](#Image-id-notes)                                   | [`AutoField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#autofield)         | `integer`                  | not null; unique; primary key |         |
| [`identifier`](#Image-identifier-notes)                   | [`UUIDField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#uuidfield)         | `uuid`                     | not null; not blank; unique   |         |
| `last_synced_with_source`                                 | [`DateTimeField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield) | `timestamp with time zone` |                               |         |
| [`license`](#Image-license-notes)                         | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(50)`              | not null; not blank           |         |
| [`license_version`](#Image-license_version-notes)         | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(25)`              |                               |         |
| `meta_data`                                               | [`JSONField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield)         | `jsonb`                    |                               |         |
| [`provider`](#Image-provider-notes)                       | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| `removed_from_source`                                     | [`BooleanField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#booleanfield)   | `boolean`                  | not null; not blank           | `False` |
| [`source`](#Image-source-notes)                           | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| [`tags`](#Image-tags-notes)                               | [`JSONField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#jsonfield)         | `jsonb`                    |                               |         |
| [`thumbnail`](#Image-thumbnail-notes)                     | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(1000)`            |                               |         |
| [`title`](#Image-title-notes)                             | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(2000)`            |                               |         |
| `updated_on`                                              | [`DateTimeField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#datetimefield) | `timestamp with time zone` | not null                      |         |
| [`url`](#Image-url-notes)                                 | [`CharField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#charfield)         | `varchar(1000)`            | unique                        |         |
| `view_count`                                              | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)   | `integer`                  |                               | `0`     |
| `watermarked`                                             | [`BooleanField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#booleanfield)   | `boolean`                  |                               |         |
| [`width`](#Image-width-notes)                             | [`IntegerField`](https://docs.djangoproject.com/en/dev/ref/models/fields/#integerfield)   | `integer`                  |                               |         |

### Notes

(Image-category-notes)=

#### `category`

**Help text:** The top-level classification of this media file.

(Image-creator-notes)=

#### `creator`

**Help text:** The name of the media creator.

(Image-creator_url-notes)=

#### `creator_url`

**Help text:** A direct link to the media creator.

(Image-filesize-notes)=

#### `filesize`

**Help text:** Number in bytes, e.g. 1024.

(Image-filetype-notes)=

#### `filetype`

**Help text:** The type of the file, related to the file extension.

(Image-foreign_identifier-notes)=

#### `foreign_identifier`

**Help text:** The identifier provided by the upstream source.

(Image-foreign_landing_url-notes)=

#### `foreign_landing_url`

**Help text:** The landing page of the work.

(Image-height-notes)=

#### `height`

**Help text:** The height of the image in pixels. Not always available.

(Image-id-notes)=

#### `id`

This is Django's automatic primary key, used for models that do not define one
explicitly.

(Image-identifier-notes)=

#### `identifier`

**Help text:** Our unique identifier for an open-licensed work.

(Image-license-notes)=

#### `license`

**Help text:** The name of license for the media.

(Image-license_version-notes)=

#### `license_version`

**Help text:** The version of the media license.

(Image-provider-notes)=

#### `provider`

**Help text:** The content provider, e.g. Flickr, Jamendo...

(Image-source-notes)=

#### `source`

**Help text:** The source of the data, meaning a particular dataset. Source and
provider can be different. Eg: the Google Open Images dataset is
source=openimages, but provider=flickr.

(Image-tags-notes)=

#### `tags`

**Help text:** Tags with detailed metadata, such as accuracy.

(Image-thumbnail-notes)=

#### `thumbnail`

**Help text:** The thumbnail for the media.

(Image-title-notes)=

#### `title`

**Help text:** The name of the media.

(Image-url-notes)=

#### `url`

**Help text:** The actual URL to the media file.

(Image-width-notes)=

#### `width`

**Help text:** The width of the image in pixels. Not always available.
