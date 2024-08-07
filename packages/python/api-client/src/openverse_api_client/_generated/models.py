"""
Openverse API client OpenAPI schema types.

This file is generated from a template. Do not edit it by hand!

See https://docs.openverse.org/packages/python/api-client/index.html#development-and-implementation-details
"""

import typing_extensions as typing

__all__ = [
    "GrantTypeEnum",
    "OAuth2KeyInfo",
    "OAuth2Token",
    "OAuth2Registration",
    "OAuth2Application",
    "OAuth2TokenRequest",
    "Source",
    "Tag",
    "AudioAltFile",
    "AudioSet",
    "AudioWaveform",
    "Audio",
    "Image",
    "PaginatedImageList",
    "PaginatedAudioList",
]


GrantTypeEnum = typing.Literal["client_credentials"]


class OAuth2KeyInfo(typing.TypedDict):
    requests_this_minute: None | int
    """
    The number of requests your key has performed in the last minute.
    """

    requests_today: None | int
    """
    The number of requests your key has performed in the last day.
    """

    rate_limit_model: str
    """
    The type of rate limit applied to your key. Can be 'standard' or 'enhanced'; enhanced users enjoy higher rate limits than their standard key counterparts. Contact Openverse if you need a higher rate limit.
    """

    verified: bool
    """
    Whether the application has verified the submitted email address.
    """


class OAuth2Token(typing.TypedDict):
    """
    Serializes the response for an access token.

    This is a dummy serializer for OpenAPI and is not actually used.
    """

    access_token: str
    """
    The access token that can be used to authenticate requests.
    """

    token_type: str
    """
    The type of token. This will always be 'Bearer'.
    """

    expires_in: int
    """
    The number of seconds until the token expires.
    """

    scope: str
    """
    The scope of the token.
    """


class OAuth2Registration(typing.TypedDict):
    name: str
    """
    A unique human-readable name for your application or project requiring access to the Openverse API.
    """

    description: str
    """
    A description of what you are trying to achieve with your project using the API. Please provide as much detail as possible!
    """

    email: str
    """
    A valid email that we can reach you at if we have any questions about your use case or data consumption.
    """


class OAuth2Application(typing.TypedDict):
    client_id: str
    """
    The unique, public identifier of your application.
    """

    client_secret: str
    """
    The secret key used to authenticate your application.
    """

    name: str
    """
    The name of your application or project.
    """

    msg: str
    """
    Some additional information about the application.
    """


class OAuth2TokenRequest(typing.TypedDict):
    """
    Serializes a request for an access token.

    This is a dummy serializer for OpenAPI and is not actually used.
    """

    client_id: str
    """
    The unique, public identifier of your application.
    """

    client_secret: str
    """
    The secret key used to authenticate your application.
    """

    grant_type: typing.Literal["client_credentials"]


class Source(typing.TypedDict):
    source_name: str
    """
    The source of the media, e.g. flickr
    """

    display_name: str
    """
    The name of content source, e.g. Flickr
    """

    source_url: str
    """
    The URL of the source, e.g. https://www.flickr.com
    """

    logo_url: None | str
    """
    The URL to a logo for the source.
    """

    media_count: int
    """
    The number of media items indexed from the source.
    """


class Tag(typing.TypedDict):
    """
    This output serializer serializes a singular tag.
    """

    name: str
    """
    The name of a detailed tag.
    """

    unstable__provider: None | str
    """
    The source of the tag. When this field matches the provider for the record, the tag originated from the upstream provider. Otherwise, the tag was added with an external machine-generated labeling processes.
    """

    accuracy: typing.NotRequired[None | float]
    """
    The accuracy of a machine-generated tag. Human-generated tags have a null accuracy field.
    """


class AudioAltFile(typing.TypedDict):
    """
    A set of alternative files for a single audio object,
    rendered as a part of the ``AudioSerializer`` output.
    """

    url: str
    """
    URL of the alternative file.
    """

    filetype: str
    """
    File type of the alternative file.
    """

    bit_rate: typing.NotRequired[int]
    """
    Bit rate of the alternative file.
    """

    filesize: typing.NotRequired[int]
    """
    Size of the alternative file in bytes.
    """

    sample_rate: typing.NotRequired[int]
    """
    Sample rate of the alternative file.
    """


class AudioSet(typing.TypedDict):
    """
    An audio set, rendered as a part of the ``AudioSerializer`` output.
    """

    title: typing.NotRequired[None | str]
    """
    The name of the media.
    """

    foreign_landing_url: typing.NotRequired[None | str]
    """
    The landing page of the work.
    """

    creator: typing.NotRequired[None | str]
    """
    The name of the media creator.
    """

    creator_url: typing.NotRequired[None | str]
    """
    A direct link to the media creator.
    """

    url: typing.NotRequired[None | str]
    """
    The actual URL to the media file.
    """

    filesize: typing.NotRequired[None | int]
    """
    Number in bytes, e.g. 1024.
    """

    filetype: typing.NotRequired[None | str]
    """
    The type of the file, related to the file extension.
    """


class AudioWaveform(typing.TypedDict):
    len: int
    points: list[float]


class Audio(typing.TypedDict):
    """
    A single audio file. Used in search results.
    """

    id: str
    """
    Our unique identifier for an open-licensed work.
    """

    indexed_on: str
    """
    The timestamp of when the media was indexed by Openverse.
    """

    license: str
    """
    The name of license for the media.
    """

    license_url: None | str
    """
    A direct link to the license deed or legal terms.
    """

    tags: None | list[Tag]
    """
    Tags with detailed metadata, such as accuracy.
    """

    alt_files: None | list[AudioAltFile]
    """
    JSON describing alternative files for this audio.
    """

    attribution: None | str
    """
    Legally valid attribution for the media item in plain-text English.
    """

    fields_matched: None | list[typing.Any]
    """
    List the fields that matched the query for this result.
    """

    mature: bool
    """
    Whether the media item is marked as mature
    """

    audio_set: None | AudioSet
    """
    Reference to set of which this track is a part.
    """

    thumbnail: None | str
    """
    A direct link to the miniature artwork.
    """

    detail_url: str
    """
    A direct link to the detail view of this audio file.
    """

    related_url: str
    """
    A link to an endpoint that provides similar audio files.
    """

    waveform: str
    """
    A direct link to the waveform peaks.
    """

    title: typing.NotRequired[None | str]
    """
    The name of the media.
    """

    foreign_landing_url: typing.NotRequired[None | str]
    """
    The landing page of the work.
    """

    url: typing.NotRequired[None | str]
    """
    The actual URL to the media file.
    """

    creator: typing.NotRequired[None | str]
    """
    The name of the media creator.
    """

    creator_url: typing.NotRequired[None | str]
    """
    A direct link to the media creator.
    """

    license_version: typing.NotRequired[None | str]
    """
    The version of the media license.
    """

    provider: typing.NotRequired[None | str]
    """
    The content provider, e.g. Flickr, Jamendo...
    """

    source: typing.NotRequired[None | str]
    """
    The source of the data, meaning a particular dataset. Source and provider can be different. Eg: the Google Open Images dataset is source=openimages, but provider=flickr.
    """

    category: typing.NotRequired[None | str]
    """
    The top-level classification of this media file.
    """

    genres: typing.NotRequired[None | list[str]]
    """
    An array of audio genres such as `rock`, `electronic` for `music` category, or `politics`, `sport`, `education` for `podcast` category
    """

    filesize: typing.NotRequired[None | int]
    """
    Number in bytes, e.g. 1024.
    """

    filetype: typing.NotRequired[None | str]
    """
    The type of the file, related to the file extension.
    """

    duration: typing.NotRequired[None | int]
    """
    The time length of the audio file in milliseconds.
    """

    bit_rate: typing.NotRequired[None | int]
    """
    Number in bits per second, eg. 128000.
    """

    sample_rate: typing.NotRequired[None | int]
    """
    Number in hertz, eg. 44100.
    """


class Image(typing.TypedDict):
    """
    A single image. Used in search results.
    """

    id: str
    """
    Our unique identifier for an open-licensed work.
    """

    indexed_on: str
    """
    The timestamp of when the media was indexed by Openverse.
    """

    license: str
    """
    The name of license for the media.
    """

    license_url: None | str
    """
    A direct link to the license deed or legal terms.
    """

    tags: None | list[Tag]
    """
    Tags with detailed metadata, such as accuracy.
    """

    attribution: None | str
    """
    Legally valid attribution for the media item in plain-text English.
    """

    fields_matched: None | list[typing.Any]
    """
    List the fields that matched the query for this result.
    """

    mature: bool
    """
    Whether the media item is marked as mature
    """

    thumbnail: str
    """
    A direct link to the miniature artwork.
    """

    detail_url: str
    """
    A direct link to the detail view of this audio file.
    """

    related_url: str
    """
    A link to an endpoint that provides similar audio files.
    """

    title: typing.NotRequired[None | str]
    """
    The name of the media.
    """

    foreign_landing_url: typing.NotRequired[None | str]
    """
    The landing page of the work.
    """

    url: typing.NotRequired[None | str]
    """
    The actual URL to the media file.
    """

    creator: typing.NotRequired[None | str]
    """
    The name of the media creator.
    """

    creator_url: typing.NotRequired[None | str]
    """
    A direct link to the media creator.
    """

    license_version: typing.NotRequired[None | str]
    """
    The version of the media license.
    """

    provider: typing.NotRequired[None | str]
    """
    The content provider, e.g. Flickr, Jamendo...
    """

    source: typing.NotRequired[None | str]
    """
    The source of the data, meaning a particular dataset. Source and provider can be different. Eg: the Google Open Images dataset is source=openimages, but provider=flickr.
    """

    category: typing.NotRequired[None | str]
    """
    The top-level classification of this media file.
    """

    filesize: typing.NotRequired[None | int]
    """
    Number in bytes, e.g. 1024.
    """

    filetype: typing.NotRequired[None | str]
    """
    The type of the file, related to the file extension.
    """

    height: typing.NotRequired[None | int]
    """
    The height of the image in pixels. Not always available.
    """

    width: typing.NotRequired[None | int]
    """
    The width of the image in pixels. Not always available.
    """


class PaginatedImageList(typing.TypedDict):
    result_count: int
    """
    The total number of items returned by search result.
    """

    page_count: int
    """
    The total number of pages returned by search result.
    """

    page_size: int
    """
    The number of items per page.
    """

    page: int
    """
    The current page number returned in the response.
    """

    results: list[Image]
    warnings: typing.NotRequired[list[typing.Any]]
    """
    Warnings pertinent to the request. If there are no warnings, this property will not be present on the response. Warnings are non-critical problems with the request. Responses with warnings should be treated as unstable. Warning descriptions must not be treated as machine readable and their schema can change at any time.
    """


class PaginatedAudioList(typing.TypedDict):
    result_count: int
    """
    The total number of items returned by search result.
    """

    page_count: int
    """
    The total number of pages returned by search result.
    """

    page_size: int
    """
    The number of items per page.
    """

    page: int
    """
    The current page number returned in the response.
    """

    results: list[Audio]
    warnings: typing.NotRequired[list[typing.Any]]
    """
    Warnings pertinent to the request. If there are no warnings, this property will not be present on the response. Warnings are non-critical problems with the request. Responses with warnings should be treated as unstable. Warning descriptions must not be treated as machine readable and their schema can change at any time.
    """
