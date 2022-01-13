from uuid import UUID

from pydantic import BaseModel, Field, validator

from analytics.models import DetailPageEvents


class SearchEventSchema(BaseModel):
    query: str = Field(description="the search query")
    session_uuid: str = Field(
        description="a unique identifier labeling an anonymous user's session"
    )

    @validator("session_uuid")
    def session_uuid_must_be_v4(cls, val):
        return UUID(val, version=4).hex

    class Config:
        schema_extra = {
            "example": {
                "query": "cat",
                "session_uuid": "00000000-0000-0000-0000-000000000000",
            }
        }


class SearchRatingEventSchema(BaseModel):
    query: str = Field(description="the search query")
    relevant: bool = Field(description="whether the search results are relevant")

    class Config:
        schema_extra = {"example": {"query": "cat", "relevant": True}}


class ResultClickEventSchema(BaseModel):
    query: str = Field(description="the search query")
    session_uuid: str = Field(
        description="a unique identifier labeling an anonymous user's session"
    )
    result_uuid: str = Field(
        description="a unique identifier for the result that was clicked"
    )
    result_rank: int = Field(
        description="the 0-indexed position of the result in the search results grid"
    )

    @validator("session_uuid")
    def session_uuid_must_be_v4(cls, val):
        return UUID(val, version=4).hex

    @validator("result_uuid")
    def result_uuid_must_be_v4(cls, val):
        return UUID(val, version=4).hex

    class Config:
        schema_extra = {
            "example": {
                "query": "cat",
                "session_uuid": "00000000-0000-0000-0000-000000000000",
                "result_uuid": "cdbd3bf6-1745-45bb-b399-61ee149cd58a",
                "result_rank": 0,
            }
        }


class DetailEventSchema(BaseModel):
    result_uuid: str = Field(
        description=(
            "the unique identifier for the detail page " "associated with the event"
        )
    )
    event_type: str = Field(
        description=(
            f"one of {', '.join([f'`{item.name}`' for item in DetailPageEvents])}"
        )
    )

    @validator("event_type")
    def event_must_be_valid_enum_item(cls, val):
        if not hasattr(DetailPageEvents, val):
            items = ", ".join([f"`{item.name}`" for item in DetailPageEvents])
            raise ValueError(f"Event type must be one of {items}")
        return val

    class Config:
        schema_extra = {
            "example": {
                "event_type": "SHARED_SOCIAL",
                "result_uuid": "cdbd3bf6-1745-45bb-b399-61ee149cd58a",
            }
        }
