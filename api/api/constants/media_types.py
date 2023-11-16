"""Also see `ingestion_server/constants/media_types.py`."""
from typing import Literal


AUDIO_TYPE = "audio"
IMAGE_TYPE = "image"

MEDIA_TYPES = [AUDIO_TYPE, IMAGE_TYPE]
MediaType = Literal["audio", "image"]

MEDIA_TYPE_CHOICES = [(AUDIO_TYPE, "Audio"), (IMAGE_TYPE, "Image")]

OriginIndex = MediaType
SearchIndex = Literal["image", "image-filtered", "audio", "audio-filtered"]
