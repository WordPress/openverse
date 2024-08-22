from typing import Literal, Any
import typing
from abc import ABC

from openverse_api_client._utils import Empty, EMPTY, is_empty


class Route(ABC):
    path: str
    method: Literal["GET", "POST"]
    content_type: str
    json_response: bool

    path_params: None | dict[str, str]
    query_params: None | dict[str, Any]
    body: None | dict[str, Any]


class v1_audio_search(Route):
    path = "/v1/audio/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        *,
        page: int | Empty = EMPTY,
        page_size: int | Empty = EMPTY,
        q: str | Empty = EMPTY,
        source: str | Empty = EMPTY,
        excluded_source: str | Empty = EMPTY,
        tags: str | Empty = EMPTY,
        title: str | Empty = EMPTY,
        creator: str | Empty = EMPTY,
        unstable__collection: typing.Literal["tag", "source", "creator"]
        | Empty = EMPTY,
        unstable__tag: str | Empty = EMPTY,
        license: str | Empty = EMPTY,
        license_type: str | Empty = EMPTY,
        filter_dead: bool | Empty = EMPTY,
        extension: str | Empty = EMPTY,
        mature: bool | Empty = EMPTY,
        unstable__sort_by: typing.Literal["relevance", "indexed_on"] | Empty = EMPTY,
        unstable__sort_dir: typing.Literal["desc", "asc"] | Empty = EMPTY,
        unstable__authority: bool | Empty = EMPTY,
        unstable__authority_boost: float | Empty = EMPTY,
        unstable__include_sensitive_results: bool | Empty = EMPTY,
        category: str | Empty = EMPTY,
        length: str | Empty = EMPTY,
        peaks: bool | Empty = EMPTY,
    ):
        self.path_params = None

        self.query_params = {}
        if not is_empty(page):
            self.query_params["page"] = page
        if not is_empty(page_size):
            self.query_params["page_size"] = page_size
        if not is_empty(q):
            self.query_params["q"] = q
        if not is_empty(source):
            self.query_params["source"] = source
        if not is_empty(excluded_source):
            self.query_params["excluded_source"] = excluded_source
        if not is_empty(tags):
            self.query_params["tags"] = tags
        if not is_empty(title):
            self.query_params["title"] = title
        if not is_empty(creator):
            self.query_params["creator"] = creator
        if not is_empty(unstable__collection):
            self.query_params["unstable__collection"] = unstable__collection
        if not is_empty(unstable__tag):
            self.query_params["unstable__tag"] = unstable__tag
        if not is_empty(license):
            self.query_params["license"] = license
        if not is_empty(license_type):
            self.query_params["license_type"] = license_type
        if not is_empty(filter_dead):
            self.query_params["filter_dead"] = filter_dead
        if not is_empty(extension):
            self.query_params["extension"] = extension
        if not is_empty(mature):
            self.query_params["mature"] = mature
        if not is_empty(unstable__sort_by):
            self.query_params["unstable__sort_by"] = unstable__sort_by
        if not is_empty(unstable__sort_dir):
            self.query_params["unstable__sort_dir"] = unstable__sort_dir
        if not is_empty(unstable__authority):
            self.query_params["unstable__authority"] = unstable__authority
        if not is_empty(unstable__authority_boost):
            self.query_params["unstable__authority_boost"] = unstable__authority_boost
        if not is_empty(unstable__include_sensitive_results):
            self.query_params["unstable__include_sensitive_results"] = (
                unstable__include_sensitive_results
            )
        if not is_empty(category):
            self.query_params["category"] = category
        if not is_empty(length):
            self.query_params["length"] = length
        if not is_empty(peaks):
            self.query_params["peaks"] = peaks

        self.body = None


class v1_audio(Route):
    path = "/v1/audio/{identifier}/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        identifier: str,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = None

        self.body = None


class v1_audio_related(Route):
    path = "/v1/audio/{identifier}/related/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        identifier: str,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = None

        self.body = None


class v1_audio_thumb(Route):
    path = "/v1/audio/{identifier}/thumb/"
    method = "GET"
    content_type = "application/json"
    json_response = False

    def __init__(
        self,
        identifier: str,
        *,
        full_size: bool | Empty = EMPTY,
        compressed: bool | Empty = EMPTY,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = {}
        if not is_empty(full_size):
            self.query_params["full_size"] = full_size
        if not is_empty(compressed):
            self.query_params["compressed"] = compressed

        self.body = None


class v1_audio_waveform(Route):
    path = "/v1/audio/{identifier}/waveform/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        identifier: str,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = None

        self.body = None


class v1_audio_stats(Route):
    path = "/v1/audio/stats/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
    ):
        self.path_params = None

        self.query_params = None

        self.body = None


class v1_auth_tokens_register(Route):
    path = "/v1/auth_tokens/register/"
    method = "POST"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        *,
        name: str,
        description: str,
        email: str,
    ):
        self.path_params = None

        self.query_params = None

        self.body = {
            "name": name,
            "description": description,
            "email": email,
        }


class v1_auth_tokens_token(Route):
    path = "/v1/auth_tokens/token/"
    method = "POST"
    content_type = "application/x-www-form-urlencoded"
    json_response = True

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        grant_type: typing.Literal["client_credentials"],
    ):
        self.path_params = None

        self.query_params = None

        self.body = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant_type,
        }


class v1_image_search(Route):
    path = "/v1/images/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        *,
        page: int | Empty = EMPTY,
        page_size: int | Empty = EMPTY,
        q: str | Empty = EMPTY,
        source: str | Empty = EMPTY,
        excluded_source: str | Empty = EMPTY,
        tags: str | Empty = EMPTY,
        title: str | Empty = EMPTY,
        creator: str | Empty = EMPTY,
        unstable__collection: typing.Literal["tag", "source", "creator"]
        | Empty = EMPTY,
        unstable__tag: str | Empty = EMPTY,
        license: str | Empty = EMPTY,
        license_type: str | Empty = EMPTY,
        filter_dead: bool | Empty = EMPTY,
        extension: str | Empty = EMPTY,
        mature: bool | Empty = EMPTY,
        unstable__sort_by: typing.Literal["relevance", "indexed_on"] | Empty = EMPTY,
        unstable__sort_dir: typing.Literal["desc", "asc"] | Empty = EMPTY,
        unstable__authority: bool | Empty = EMPTY,
        unstable__authority_boost: float | Empty = EMPTY,
        unstable__include_sensitive_results: bool | Empty = EMPTY,
        category: str | Empty = EMPTY,
        aspect_ratio: str | Empty = EMPTY,
        size: str | Empty = EMPTY,
    ):
        self.path_params = None

        self.query_params = {}
        if not is_empty(page):
            self.query_params["page"] = page
        if not is_empty(page_size):
            self.query_params["page_size"] = page_size
        if not is_empty(q):
            self.query_params["q"] = q
        if not is_empty(source):
            self.query_params["source"] = source
        if not is_empty(excluded_source):
            self.query_params["excluded_source"] = excluded_source
        if not is_empty(tags):
            self.query_params["tags"] = tags
        if not is_empty(title):
            self.query_params["title"] = title
        if not is_empty(creator):
            self.query_params["creator"] = creator
        if not is_empty(unstable__collection):
            self.query_params["unstable__collection"] = unstable__collection
        if not is_empty(unstable__tag):
            self.query_params["unstable__tag"] = unstable__tag
        if not is_empty(license):
            self.query_params["license"] = license
        if not is_empty(license_type):
            self.query_params["license_type"] = license_type
        if not is_empty(filter_dead):
            self.query_params["filter_dead"] = filter_dead
        if not is_empty(extension):
            self.query_params["extension"] = extension
        if not is_empty(mature):
            self.query_params["mature"] = mature
        if not is_empty(unstable__sort_by):
            self.query_params["unstable__sort_by"] = unstable__sort_by
        if not is_empty(unstable__sort_dir):
            self.query_params["unstable__sort_dir"] = unstable__sort_dir
        if not is_empty(unstable__authority):
            self.query_params["unstable__authority"] = unstable__authority
        if not is_empty(unstable__authority_boost):
            self.query_params["unstable__authority_boost"] = unstable__authority_boost
        if not is_empty(unstable__include_sensitive_results):
            self.query_params["unstable__include_sensitive_results"] = (
                unstable__include_sensitive_results
            )
        if not is_empty(category):
            self.query_params["category"] = category
        if not is_empty(aspect_ratio):
            self.query_params["aspect_ratio"] = aspect_ratio
        if not is_empty(size):
            self.query_params["size"] = size

        self.body = None


class v1_image(Route):
    path = "/v1/images/{identifier}/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        identifier: str,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = None

        self.body = None


class v1_image_related(Route):
    path = "/v1/images/{identifier}/related/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
        identifier: str,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = None

        self.body = None


class v1_image_thumb(Route):
    path = "/v1/images/{identifier}/thumb/"
    method = "GET"
    content_type = "application/json"
    json_response = False

    def __init__(
        self,
        identifier: str,
        *,
        full_size: bool | Empty = EMPTY,
        compressed: bool | Empty = EMPTY,
    ):
        self.path_params = {
            "identifier": identifier,
        }

        self.query_params = {}
        if not is_empty(full_size):
            self.query_params["full_size"] = full_size
        if not is_empty(compressed):
            self.query_params["compressed"] = compressed

        self.body = None


class v1_image_stats(Route):
    path = "/v1/images/stats/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
    ):
        self.path_params = None

        self.query_params = None

        self.body = None


class v1_rate_limit(Route):
    path = "/v1/rate_limit/"
    method = "GET"
    content_type = "application/json"
    json_response = True

    def __init__(
        self,
    ):
        self.path_params = None

        self.query_params = None

        self.body = None


ROUTES_BY_ENDPOINT = {
    "GET /v1/audio/": v1_audio_search,
    "GET /v1/audio/{identifier}/": v1_audio,
    "GET /v1/audio/{identifier}/related/": v1_audio_related,
    "GET /v1/audio/{identifier}/thumb/": v1_audio_thumb,
    "GET /v1/audio/{identifier}/waveform/": v1_audio_waveform,
    "GET /v1/audio/stats/": v1_audio_stats,
    "POST /v1/auth_tokens/register/": v1_auth_tokens_register,
    "POST /v1/auth_tokens/token/": v1_auth_tokens_token,
    "GET /v1/images/": v1_image_search,
    "GET /v1/images/{identifier}/": v1_image,
    "GET /v1/images/{identifier}/related/": v1_image_related,
    "GET /v1/images/{identifier}/thumb/": v1_image_thumb,
    "GET /v1/images/stats/": v1_image_stats,
    "GET /v1/rate_limit/": v1_rate_limit,
}
