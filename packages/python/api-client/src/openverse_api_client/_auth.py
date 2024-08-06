import asyncio
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Union, cast

import httpx

from openverse_api_client._generated.models import OAuth2Token


if TYPE_CHECKING:
    from openverse_api_client import AsyncOpenverseClient, OpenverseClient


__all__ = ["OpenverseAuth"]


class OpenverseAuth(httpx.Auth):
    EXPIRY_THRESHOLD = timedelta(seconds=5)

    credentials: dict[str, str]
    token: OAuth2Token | None = None
    expiry: datetime | None = None

    _token_refreshed: asyncio.Event

    def __init__(
        self,
        client: Union["AsyncOpenverseClient", "OpenverseClient"],
        client_id: str,
        client_secret: str,
    ):
        self.client = client.unauthed()
        self.credentials = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        self._token_refreshed = asyncio.Event()

    def _utcnow(self) -> datetime:
        return datetime.now(UTC)

    def sync_is_requesting(self) -> bool:
        """
        Whether the synchronous client is requesting a token.

        May be overridden in a multi-process environment to read
        a lock stored elsewhere (e.g., Redis)
        """
        return False

    async def async_is_requesting(self) -> bool:
        return self._token_refreshed.is_set()

    def sync_wait_for_token(self) -> Iterator[None]:
        while self.sync_is_requesting():
            yield

    async def async_wait_for_token(self):
        return await self._token_refreshed.wait()

    def _must_wait(self) -> bool:
        return (
            self.token is None or self.expiry is None or self.expiry <= self._utcnow()
        )

    def sync_must_wait(self) -> bool:
        return self._must_wait()

    async def async_must_wait(self) -> bool:
        return self._must_wait()

    def _should_refresh(self) -> bool:
        return (
            self.token is None
            or self.expiry is None
            or self.expiry - self.EXPIRY_THRESHOLD < self._utcnow()
        )

    def sync_should_refresh(self) -> bool:
        return self._should_refresh()

    async def async_should_refresh(self) -> bool:
        return self._should_refresh()

    def _get_token(self) -> str:
        return cast(OAuth2Token, self.token)["access_token"]

    def sync_get_token(self) -> str:
        """
        Retrieve the Openverse API token.

        Override to retrieve the token from somewhere other than the default location,
        e.g., Redis.
        """
        return self._get_token()

    async def async_get_token(self) -> str:
        """
        Retrieve the Openverse API token.

        Override to retrieve the token from somewhere other than the default location.
        e.g., Redis.
        """
        return self._get_token()

    def sync_refresh(self):
        token_response = self.client.v1_auth_tokens_token(**self.credentials)

        self.token = token_response.body
        self.expiry = self._utcnow() + timedelta(seconds=self.token.expires_in)

    async def async_refresh(self):
        self._token_refreshed.clear()
        try:
            token_response = await self.client.v1_auth_tokens_token(
                **self.credentials,
                timeout=2.0,
            )

            self.token = token_response.body
            self.expiry = self._utcnow() + timedelta(seconds=self.token.expires_in)
        finally:
            self._token_refreshed.set()

    def with_token(self, request: httpx.Request, token: str) -> httpx.Request:
        request.headers["authorization"] = f"Bearer {token}"
        return request

    def sync_auth_flow(self, request: httpx.Request):
        if not self.sync_is_requesting() and self.sync_should_refresh():
            self.sync_refresh()

        if self.sync_must_wait():
            wait = self.sync_wait_for_token()
            while next(wait, None):
                continue

        token = self.sync_get_token()
        yield self.with_token(request, token)

    async def async_auth_flow(self, request: httpx.Request):
        if not await self.async_is_requesting() and await self.async_should_refresh():
            loop = asyncio.get_running_loop()
            loop.create_task(self.async_refresh())

        if await self.async_must_wait():
            await self.async_wait_for_token()

        token = await self.async_get_token()
        yield self.with_token(request, token)
