"""
Fully typed Openverse API client.

This file is generated from a template. Do not edit it by hand!

See https://docs.openverse.org/packages/python/api-client/index.html#development-and-implementation-details
"""

from typing_extensions import cast, Self
import typing_extensions as typing
import httpx

from openverse_api_client._generated.models import (
    OAuth2KeyInfo,
    OAuth2Token,
    OAuth2Application,
    Source,
    AudioWaveform,
    Audio,
    Image,
    PaginatedImageList,
    PaginatedAudioList,
)
from openverse_api_client._auth import OpenverseAuth
from openverse_api_client._response import Response, Request
from openverse_api_client._utils import Empty, EMPTY, is_empty


EXPIRY_THRESHOLD = 30


class AsyncOpenverseClient:
    base_url: str = "https://api.openverse.org"
    auth: OpenverseAuth | None = None
    client: httpx.AsyncClient

    _is_shared_client: bool

    def __init__(
        self,
        base_url: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ):
        self.base_url = base_url if base_url else self.base_url
        if self.base_url[-1] == "/":
            self.base_url = self.base_url[:-1]

        if httpx_client is None:
            self.client = httpx.AsyncClient()
            self._is_shared_client = False
        else:
            self.client = httpx_client
            self._is_shared_client = True

        if client_id or client_secret:
            if not client_id and client_secret:
                raise ValueError(
                    "`client_id` and `client_secret` are both required when either is defined"
                )

            self.auth = OpenverseAuth(
                client=self,
                client_id=typing.cast(str, client_id),
                client_secret=typing.cast(str, client_secret),
            )

    def unauthed(self) -> Self:
        return cast(
            Self,
            AsyncOpenverseClient(
                base_url=self.base_url,
                httpx_client=self.client,
            ),
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type=None, exc_value=None, traceback=None) -> None:
        await self.client.__aexit__(exc_type, exc_value, traceback)

    async def close(self):
        await self.client.aclose()

    async def _base_request(
        self,
        *,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        return await self.client.request(
            method=method,
            url=f"{self.base_url}{path}",
            **kwargs,
        )

    async def _request(
        self,
        *,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        kwargs.setdefault("auth", self.auth)
        return await self._base_request(
            method=method,
            path=path,
            **kwargs,
        )

    async def v1_audio_search(
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
        headers: dict | httpx.Headers | None = None,
    ) -> Response[PaginatedAudioList]:
        path = "/v1/audio/"
        params: dict[str, typing.Any] = {}
        if not is_empty(page):
            params["page"] = page
        if not is_empty(page_size):
            params["page_size"] = page_size
        if not is_empty(q):
            params["q"] = q
        if not is_empty(source):
            params["source"] = source
        if not is_empty(excluded_source):
            params["excluded_source"] = excluded_source
        if not is_empty(tags):
            params["tags"] = tags
        if not is_empty(title):
            params["title"] = title
        if not is_empty(creator):
            params["creator"] = creator
        if not is_empty(unstable__collection):
            params["unstable__collection"] = unstable__collection
        if not is_empty(unstable__tag):
            params["unstable__tag"] = unstable__tag
        if not is_empty(license):
            params["license"] = license
        if not is_empty(license_type):
            params["license_type"] = license_type
        if not is_empty(filter_dead):
            params["filter_dead"] = filter_dead
        if not is_empty(extension):
            params["extension"] = extension
        if not is_empty(mature):
            params["mature"] = mature
        if not is_empty(unstable__sort_by):
            params["unstable__sort_by"] = unstable__sort_by
        if not is_empty(unstable__sort_dir):
            params["unstable__sort_dir"] = unstable__sort_dir
        if not is_empty(unstable__authority):
            params["unstable__authority"] = unstable__authority
        if not is_empty(unstable__authority_boost):
            params["unstable__authority_boost"] = unstable__authority_boost
        if not is_empty(unstable__include_sensitive_results):
            params["unstable__include_sensitive_results"] = (
                unstable__include_sensitive_results
            )
        if not is_empty(category):
            params["category"] = category
        if not is_empty(length):
            params["length"] = length
        if not is_empty(peaks):
            params["peaks"] = peaks

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[PaginatedAudioList](
            body=typing.cast(PaginatedAudioList, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_audio(
        self,
        identifier: str,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[Audio]:
        path = "/v1/audio/{identifier}/".format(
            identifier=identifier,
        )

        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[Audio](
            body=typing.cast(Audio, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_audio_related(
        self,
        identifier: str,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[PaginatedAudioList]:
        path = "/v1/audio/{identifier}/related/".format(
            identifier=identifier,
        )

        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[PaginatedAudioList](
            body=typing.cast(PaginatedAudioList, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_audio_thumb(
        self,
        identifier: str,
        *,
        full_size: bool | Empty = EMPTY,
        compressed: bool | Empty = EMPTY,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[bytes]:
        path = "/v1/audio/{identifier}/thumb/".format(
            identifier=identifier,
        )

        params: dict[str, typing.Any] = {}
        if not is_empty(full_size):
            params["full_size"] = full_size
        if not is_empty(compressed):
            params["compressed"] = compressed

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.content
        return Response[bytes](
            body=typing.cast(bytes, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_audio_waveform(
        self,
        identifier: str,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[AudioWaveform]:
        path = "/v1/audio/{identifier}/waveform/".format(
            identifier=identifier,
        )

        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[AudioWaveform](
            body=typing.cast(AudioWaveform, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_audio_stats(
        self,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[list[Source]]:
        path = "/v1/audio/stats/"
        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[list[Source]](
            body=typing.cast(list[Source], content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_auth_tokens_register(
        self,
        *,
        name: str,
        description: str,
        email: str,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[OAuth2Application]:
        path = "/v1/auth_tokens/register/"
        params = None

        body: dict[str, typing.Any] = {
            "name": name,
            "description": description,
            "email": email,
        }

        response = await self._request(
            method="post",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[OAuth2Application](
            body=typing.cast(OAuth2Application, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_auth_tokens_token(
        self,
        *,
        client_id: str,
        client_secret: str,
        grant_type: typing.Literal["client_credentials"],
        headers: dict | httpx.Headers | None = None,
    ) -> Response[OAuth2Token]:
        path = "/v1/auth_tokens/token/"
        params = None

        body: dict[str, typing.Any] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": grant_type,
        }

        response = await self._request(
            method="post",
            path=path,
            params=params,
            data=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[OAuth2Token](
            body=typing.cast(OAuth2Token, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_image_search(
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
        headers: dict | httpx.Headers | None = None,
    ) -> Response[PaginatedImageList]:
        path = "/v1/images/"
        params: dict[str, typing.Any] = {}
        if not is_empty(page):
            params["page"] = page
        if not is_empty(page_size):
            params["page_size"] = page_size
        if not is_empty(q):
            params["q"] = q
        if not is_empty(source):
            params["source"] = source
        if not is_empty(excluded_source):
            params["excluded_source"] = excluded_source
        if not is_empty(tags):
            params["tags"] = tags
        if not is_empty(title):
            params["title"] = title
        if not is_empty(creator):
            params["creator"] = creator
        if not is_empty(unstable__collection):
            params["unstable__collection"] = unstable__collection
        if not is_empty(unstable__tag):
            params["unstable__tag"] = unstable__tag
        if not is_empty(license):
            params["license"] = license
        if not is_empty(license_type):
            params["license_type"] = license_type
        if not is_empty(filter_dead):
            params["filter_dead"] = filter_dead
        if not is_empty(extension):
            params["extension"] = extension
        if not is_empty(mature):
            params["mature"] = mature
        if not is_empty(unstable__sort_by):
            params["unstable__sort_by"] = unstable__sort_by
        if not is_empty(unstable__sort_dir):
            params["unstable__sort_dir"] = unstable__sort_dir
        if not is_empty(unstable__authority):
            params["unstable__authority"] = unstable__authority
        if not is_empty(unstable__authority_boost):
            params["unstable__authority_boost"] = unstable__authority_boost
        if not is_empty(unstable__include_sensitive_results):
            params["unstable__include_sensitive_results"] = (
                unstable__include_sensitive_results
            )
        if not is_empty(category):
            params["category"] = category
        if not is_empty(aspect_ratio):
            params["aspect_ratio"] = aspect_ratio
        if not is_empty(size):
            params["size"] = size

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[PaginatedImageList](
            body=typing.cast(PaginatedImageList, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_image(
        self,
        identifier: str,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[Image]:
        path = "/v1/images/{identifier}/".format(
            identifier=identifier,
        )

        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[Image](
            body=typing.cast(Image, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_image_related(
        self,
        identifier: str,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[Image]:
        path = "/v1/images/{identifier}/related/".format(
            identifier=identifier,
        )

        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[Image](
            body=typing.cast(Image, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_image_thumb(
        self,
        identifier: str,
        *,
        full_size: bool | Empty = EMPTY,
        compressed: bool | Empty = EMPTY,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[bytes]:
        path = "/v1/images/{identifier}/thumb/".format(
            identifier=identifier,
        )

        params: dict[str, typing.Any] = {}
        if not is_empty(full_size):
            params["full_size"] = full_size
        if not is_empty(compressed):
            params["compressed"] = compressed

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.content
        return Response[bytes](
            body=typing.cast(bytes, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_image_stats(
        self,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[list[Source]]:
        path = "/v1/images/stats/"
        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[list[Source]](
            body=typing.cast(list[Source], content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )

    async def v1_rate_limit(
        self,
        *,
        headers: dict | httpx.Headers | None = None,
    ) -> Response[OAuth2KeyInfo]:
        path = "/v1/rate_limit/"
        params = None

        body = None

        response = await self._request(
            method="get",
            path=path,
            params=params,
            json=body,
            headers=headers,
        )

        await response.aread()
        content = response.json()
        return Response[OAuth2KeyInfo](
            body=typing.cast(OAuth2KeyInfo, content),
            status_code=response.status_code,
            headers=response.headers,
            request=Request(
                headers=response.request.headers,
                content=response.request.content,
                url=str(response.request.url),
                method=response.request.method,
            ),
        )
