from dataclasses import dataclass
from uuid import UUID


@dataclass
class MediaInfo:
    media_provider: str
    media_identifier: UUID
    image_url: str


@dataclass
class RequestConfig:
    accept_header: str = "image/*"
    is_full_size: bool = False
    is_compressed: bool = True
