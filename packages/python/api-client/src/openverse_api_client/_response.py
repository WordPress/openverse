from dataclasses import dataclass
from typing import Generic, TypeVar

from httpx import Headers


__all__ = [
    "Request",
    "Response",
]


@dataclass
class Request:
    headers: Headers
    method: str
    content: bytes
    url: str


Body = TypeVar("Body")


@dataclass
class Response(Generic[Body]):
    body: Body
    status_code: int
    headers: Headers
    request: Request
