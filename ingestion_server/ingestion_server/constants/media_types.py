"""Also see `api/constants/media_types.py`."""

from typing import Literal, get_args


AUDIO_TYPE = "audio"
IMAGE_TYPE = "image"
MODEL_3D_TYPE = "model_3d"

MediaType = Literal["audio", "image", "model_3d"]

MEDIA_TYPES: list[MediaType] = list(get_args(MediaType))
