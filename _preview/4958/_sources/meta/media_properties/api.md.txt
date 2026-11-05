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

**Models**:

- [Audio](#audio)
- [Image](#image)

## Audio

### Relations

| Name                                                        | Type                                                                                             | DB type | Nature       | To                     |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------- | ------------ | ---------------------- |
| [`audio_report`](#Audio-audio_report-notes)                 | [`ForeignKey`](https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey)           | `uuid`  | One To Many  | `AudioReport`          |
| [`audiodecision`](#Audio-audiodecision-notes)               | [`ManyToManyField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#manytomanyfield) |         | Many To Many | `AudioDecision`        |
| [`audiodecisionthrough`](#Audio-audiodecisionthrough-notes) | [`ForeignKey`](https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey)           | `uuid`  | One To Many  | `AudioDecisionThrough` |
| [`audioset`](#Audio-audioset-notes)                         | `ForeignObject`                                                                                  |         | Many To One  | `AudioSet`             |
| [`deleted_audio`](#Audio-deleted_audio-notes)               | [`OneToOneField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `DeletedAudio`         |
| [`lists`](#Audio-lists-notes)                               | [`ManyToManyField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#manytomanyfield) |         | Many To Many | `AudioList`            |
| [`sensitive_audio`](#Audio-sensitive_audio-notes)           | [`OneToOneField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `SensitiveAudio`       |

### Values

| Name                                                                        | Type                                                                                                                                                                                     | DB type                    | Constraints                   | Default |
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ----------------------------- | ------- |
| [`alt_files`](#Audio-alt_files-notes)                                       | [`JSONField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield)                                                                                                     | `jsonb`                    |                               |         |
| [`audio_set_foreign_identifier`](#Audio-audio_set_foreign_identifier-notes) | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| [`audio_set_position`](#Audio-audio_set_position-notes)                     | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)                                                                                               | `integer`                  |                               |         |
| [`bit_rate`](#Audio-bit_rate-notes)                                         | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)                                                                                               | `integer`                  |                               |         |
| [`category`](#Audio-category-notes)                                         | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)                                                                                                     | `varchar(80)`              |                               |         |
| `created_on`                                                                | [`DateTimeField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#datetimefield)                                                                                             | `timestamp with time zone` | not null                      |         |
| [`creator`](#Audio-creator-notes)                                           | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| [`creator_url`](#Audio-creator_url-notes)                                   | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| [`duration`](#Audio-duration-notes)                                         | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)                                                                                               | `integer`                  |                               |         |
| [`filesize`](#Audio-filesize-notes)                                         | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)                                                                                               | `integer`                  |                               |         |
| [`filetype`](#Audio-filetype-notes)                                         | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)                                                                                                     | `varchar(80)`              |                               |         |
| [`foreign_identifier`](#Audio-foreign_identifier-notes)                     | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| [`foreign_landing_url`](#Audio-foreign_landing_url-notes)                   | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| [`genres`](#Audio-genres-notes)                                             | [`ArrayField`](https://docs.djangoproject.com/en/stable/ref/contrib/postgres/fields/#arrayfield) of [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield) | `varchar(80)[]`            | not blank                     |         |
| [`id`](#Audio-id-notes)                                                     | [`AutoField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#autofield)                                                                                                     | `integer`                  | not null; unique; primary key |         |
| [`identifier`](#Audio-identifier-notes)                                     | [`UUIDField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#uuidfield)                                                                                                     | `uuid`                     | not null; not blank; unique   |         |
| [`last_synced_with_source`](#Audio-last_synced_with_source-notes)           | [`DateTimeField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#datetimefield)                                                                                             | `timestamp with time zone` |                               |         |
| [`license`](#Audio-license-notes)                                           | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)                                                                                                     | `varchar(50)`              | not null; not blank           |         |
| [`license_version`](#Audio-license_version-notes)                           | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)                                                                                                     | `varchar(25)`              |                               |         |
| [`meta_data`](#Audio-meta_data-notes)                                       | [`JSONField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield)                                                                                                     | `jsonb`                    |                               |         |
| [`provider`](#Audio-provider-notes)                                         | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)                                                                                                     | `varchar(80)`              |                               |         |
| [`removed_from_source`](#Audio-removed_from_source-notes)                   | [`BooleanField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#booleanfield)                                                                                               | `boolean`                  | not null; not blank           | `False` |
| [`sample_rate`](#Audio-sample_rate-notes)                                   | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)                                                                                               | `integer`                  |                               |         |
| [`source`](#Audio-source-notes)                                             | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)                                                                                                     | `varchar(80)`              |                               |         |
| [`tags`](#Audio-tags-notes)                                                 | [`JSONField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield)                                                                                                     | `jsonb`                    |                               |         |
| [`thumbnail`](#Audio-thumbnail-notes)                                       | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| [`title`](#Audio-title-notes)                                               | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     |                               |         |
| `updated_on`                                                                | [`DateTimeField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#datetimefield)                                                                                             | `timestamp with time zone` | not null                      |         |
| [`url`](#Audio-url-notes)                                                   | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)                                                                                                     | `text`                     | unique                        |         |
| [`view_count`](#Audio-view_count-notes)                                     | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)                                                                                               | `integer`                  |                               | `0`     |
| [`watermarked`](#Audio-watermarked-notes)                                   | [`BooleanField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#booleanfield)                                                                                               | `boolean`                  |                               |         |

### Notes

(Audio-alt_files-notes)=

#### `alt_files`

**Help text:** JSON object containing information on alternative audio files.
Each object is expected to contain:

- `url`: URL reference to the file
- `filesize`: File size in bytes
- `filetype`: Extension of the file
- `bit_rate`: Bitrate of the file in bits/second
- `sample_rate`: Sample rate of the file in bits/second

(Audio-audio_report-notes)=

#### `audio_report`

**`AudioReport` docstring:** User-submitted reports of audio tracks.

`AudioDecision` is populated only if moderators have made a decision for this
report.

(Audio-audio_set_foreign_identifier-notes)=

#### `audio_set_foreign_identifier`

**Help text:** Reference to set of which this track is a part.

(Audio-audio_set_position-notes)=

#### `audio_set_position`

**Help text:** Ordering of the audio in the set.

(Audio-audiodecision-notes)=

#### `audiodecision`

**`AudioDecision` docstring:** Moderation decisions taken for audio tracks.

(Audio-audiodecisionthrough-notes)=

#### `audiodecisionthrough`

**`AudioDecisionThrough` docstring:** Many-to-many reference table for audio
decisions.

This is made explicit (rather than using Django's default) so that the audio can
be referenced by `identifier` rather than an arbitrary `id`.

(Audio-audioset-notes)=

#### `audioset`

This is a virtual foreign-key to `AudioSet` built on top of the fields
`audio_set_foreign_identifier` and `provider`.

**`AudioSet` docstring:** This is an ordered collection of audio files, such as
a podcast series or an album.

Not to be confused with `AudioList` which is a many-to-many collection of audio
files, like a playlist or favourites library.

The FileMixin inherited by this model refers not to audio but album art.

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

(Audio-deleted_audio-notes)=

#### `deleted_audio`

**`DeletedAudio` docstring:** Audio tracks deleted from the upstream source.

Do not create instances of this model manually. Create an `AudioReport` instance
instead.

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

(Audio-last_synced_with_source-notes)=

#### `last_synced_with_source`

**Help text:** The date the media was last updated from the upstream source.

(Audio-license-notes)=

#### `license`

**Help text:** The name of license for the media.

(Audio-license_version-notes)=

#### `license_version`

**Help text:** The version of the media license.

(Audio-lists-notes)=

#### `lists`

**`AudioList` docstring:** A list of audio files. Currently unused.

(Audio-meta_data-notes)=

#### `meta_data`

**Help text:** JSON object containing extra data about the media item. No fields
are expected, but if the `license_url` field is available, it will be used for
determining the license URL for the media item. The `description` field, if
available, is also indexed into Elasticsearch and as a search field on queries.

(Audio-provider-notes)=

#### `provider`

**Help text:** The content provider, e.g. Flickr, Jamendo...

(Audio-removed_from_source-notes)=

#### `removed_from_source`

**Help text:** Whether the media has been removed from the upstream source.

(Audio-sample_rate-notes)=

#### `sample_rate`

**Help text:** Number in hertz, eg. 44100.

(Audio-sensitive_audio-notes)=

#### `sensitive_audio`

**`SensitiveAudio` docstring:** Audio tracks with verified sensitivity reports.

Do not create instances of this model manually. Create an `AudioReport` instance
instead.

(Audio-source-notes)=

#### `source`

**Help text:** The source of the data, meaning a particular dataset. Source and
provider can be different. Eg: the Google Open Images dataset is
source=openimages, but provider=flickr.

(Audio-tags-notes)=

#### `tags`

**Help text:** JSON array of objects containing tags for the media. Each tag
object is expected to have:

- `name`: The tag itself (e.g. "dog")
- `provider`: The source of the tag
- `accuracy`: If the tag was added using a machine-labeler, the confidence for
  that label expressed as a value between 0 and 1.

Note that only `name` and `accuracy` are presently surfaced in API results.

(Audio-thumbnail-notes)=

#### `thumbnail`

**Help text:** The thumbnail for the media.

(Audio-title-notes)=

#### `title`

**Help text:** The name of the media.

(Audio-url-notes)=

#### `url`

**Help text:** The actual URL to the media file.

(Audio-view_count-notes)=

#### `view_count`

**Help text:** Vestigial field, purpose unknown.

(Audio-watermarked-notes)=

#### `watermarked`

**Help text:** Whether the media contains a watermark. Not currently leveraged.

## Image

### Relations

| Name                                                        | Type                                                                                             | DB type | Nature       | To                     |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ------- | ------------ | ---------------------- |
| [`deleted_image`](#Image-deleted_image-notes)               | [`OneToOneField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `DeletedImage`         |
| [`image_report`](#Image-image_report-notes)                 | [`ForeignKey`](https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey)           | `uuid`  | One To Many  | `ImageReport`          |
| [`imagedecision`](#Image-imagedecision-notes)               | [`ManyToManyField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#manytomanyfield) |         | Many To Many | `ImageDecision`        |
| [`imagedecisionthrough`](#Image-imagedecisionthrough-notes) | [`ForeignKey`](https://docs.djangoproject.com/en/stable/ref/models/fields/#foreignkey)           | `uuid`  | One To Many  | `ImageDecisionThrough` |
| [`lists`](#Image-lists-notes)                               | [`ManyToManyField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#manytomanyfield) |         | Many To Many | `ImageList`            |
| [`sensitive_image`](#Image-sensitive_image-notes)           | [`OneToOneField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#onetoonefield)     | `uuid`  | One To One   | `SensitiveImage`       |

### Values

| Name                                                              | Type                                                                                         | DB type                    | Constraints                   | Default |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------------------------- | ----------------------------- | ------- |
| [`category`](#Image-category-notes)                               | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| `created_on`                                                      | [`DateTimeField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#datetimefield) | `timestamp with time zone` | not null                      |         |
| [`creator`](#Image-creator-notes)                                 | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     |                               |         |
| [`creator_url`](#Image-creator_url-notes)                         | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     |                               |         |
| [`filesize`](#Image-filesize-notes)                               | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)   | `integer`                  |                               |         |
| [`filetype`](#Image-filetype-notes)                               | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| [`foreign_identifier`](#Image-foreign_identifier-notes)           | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     |                               |         |
| [`foreign_landing_url`](#Image-foreign_landing_url-notes)         | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     |                               |         |
| [`height`](#Image-height-notes)                                   | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)   | `integer`                  |                               |         |
| [`id`](#Image-id-notes)                                           | [`AutoField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#autofield)         | `integer`                  | not null; unique; primary key |         |
| [`identifier`](#Image-identifier-notes)                           | [`UUIDField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#uuidfield)         | `uuid`                     | not null; not blank; unique   |         |
| [`last_synced_with_source`](#Image-last_synced_with_source-notes) | [`DateTimeField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#datetimefield) | `timestamp with time zone` |                               |         |
| [`license`](#Image-license-notes)                                 | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)         | `varchar(50)`              | not null; not blank           |         |
| [`license_version`](#Image-license_version-notes)                 | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)         | `varchar(25)`              |                               |         |
| [`meta_data`](#Image-meta_data-notes)                             | [`JSONField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield)         | `jsonb`                    |                               |         |
| [`provider`](#Image-provider-notes)                               | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| [`removed_from_source`](#Image-removed_from_source-notes)         | [`BooleanField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#booleanfield)   | `boolean`                  | not null; not blank           | `False` |
| [`source`](#Image-source-notes)                                   | [`CharField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#charfield)         | `varchar(80)`              |                               |         |
| [`tags`](#Image-tags-notes)                                       | [`JSONField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#jsonfield)         | `jsonb`                    |                               |         |
| [`thumbnail`](#Image-thumbnail-notes)                             | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     |                               |         |
| [`title`](#Image-title-notes)                                     | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     |                               |         |
| `updated_on`                                                      | [`DateTimeField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#datetimefield) | `timestamp with time zone` | not null                      |         |
| [`url`](#Image-url-notes)                                         | [`TextField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#textfield)         | `text`                     | unique                        |         |
| [`view_count`](#Image-view_count-notes)                           | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)   | `integer`                  |                               | `0`     |
| [`watermarked`](#Image-watermarked-notes)                         | [`BooleanField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#booleanfield)   | `boolean`                  |                               |         |
| [`width`](#Image-width-notes)                                     | [`IntegerField`](https://docs.djangoproject.com/en/stable/ref/models/fields/#integerfield)   | `integer`                  |                               |         |

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

(Image-deleted_image-notes)=

#### `deleted_image`

**`DeletedImage` docstring:** Images deleted from the upstream source.

Do not create instances of this model manually. Create an `ImageReport` instance
instead.

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

(Image-image_report-notes)=

#### `image_report`

**`ImageReport` docstring:** User-submitted report of an image.

This contains an `ImageDecision` as well, if moderators have made a decision for
this report.

(Image-imagedecision-notes)=

#### `imagedecision`

**`ImageDecision` docstring:** Moderation decisions taken for images.

(Image-imagedecisionthrough-notes)=

#### `imagedecisionthrough`

**`ImageDecisionThrough` docstring:** Many-to-many reference table for image
decisions.

This is made explicit (rather than using Django's default) so that the image can
be referenced by `identifier` rather than an arbitrary `id`.

(Image-last_synced_with_source-notes)=

#### `last_synced_with_source`

**Help text:** The date the media was last updated from the upstream source.

(Image-license-notes)=

#### `license`

**Help text:** The name of license for the media.

(Image-license_version-notes)=

#### `license_version`

**Help text:** The version of the media license.

(Image-lists-notes)=

#### `lists`

**`ImageList` docstring:** A list of images. Currently unused.

(Image-meta_data-notes)=

#### `meta_data`

**Help text:** JSON object containing extra data about the media item. No fields
are expected, but if the `license_url` field is available, it will be used for
determining the license URL for the media item. The `description` field, if
available, is also indexed into Elasticsearch and as a search field on queries.

(Image-provider-notes)=

#### `provider`

**Help text:** The content provider, e.g. Flickr, Jamendo...

(Image-removed_from_source-notes)=

#### `removed_from_source`

**Help text:** Whether the media has been removed from the upstream source.

(Image-sensitive_image-notes)=

#### `sensitive_image`

**`SensitiveImage` docstring:** Images with verified sensitivity reports.

Do not create instances of this model manually. Create an `ImageReport` instance
instead.

(Image-source-notes)=

#### `source`

**Help text:** The source of the data, meaning a particular dataset. Source and
provider can be different. Eg: the Google Open Images dataset is
source=openimages, but provider=flickr.

(Image-tags-notes)=

#### `tags`

**Help text:** JSON array of objects containing tags for the media. Each tag
object is expected to have:

- `name`: The tag itself (e.g. "dog")
- `provider`: The source of the tag
- `accuracy`: If the tag was added using a machine-labeler, the confidence for
  that label expressed as a value between 0 and 1.

Note that only `name` and `accuracy` are presently surfaced in API results.

(Image-thumbnail-notes)=

#### `thumbnail`

**Help text:** The thumbnail for the media.

(Image-title-notes)=

#### `title`

**Help text:** The name of the media.

(Image-url-notes)=

#### `url`

**Help text:** The actual URL to the media file.

(Image-view_count-notes)=

#### `view_count`

**Help text:** Vestigial field, purpose unknown.

(Image-watermarked-notes)=

#### `watermarked`

**Help text:** Whether the media contains a watermark. Not currently leveraged.

(Image-width-notes)=

#### `width`

**Help text:** The width of the image in pixels. Not always available.
