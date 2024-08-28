# Type definitions for the sample data
from typing import NamedTuple, Type, TypedDict

from psycopg2.extras import Json


TagsBuffer: Type = list[tuple[str, Json]]


class Label(TypedDict, total=False):
    Name: str
    Confidence: float


class Response(TypedDict, total=False):
    Labels: list[Label]


class LabeledImage(TypedDict, total=False):
    image_uuid: str
    response: Response


class MachineGeneratedTag(TypedDict):
    name: str
    accuracy: float
    provider: str


class ParseResults(NamedTuple):
    total_processed: int
    total_skipped: int
    failed_records: list[str]
