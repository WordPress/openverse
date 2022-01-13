from pydantic import BaseModel, Field


class OkSchema(BaseModel):
    status: str = Field(
        default="200 OK",
        description="synonymous with the HTTP status-code of the response",
    )


class CreatedSchema(BaseModel):
    status: str = Field(
        default="201 Created",
        description="synonymous with the HTTP status-code of the response",
    )


class BadRequestSchema(BaseModel):
    class BadRequestSchemaElement(BaseModel):
        loc: list[str] = Field(description="the fields that did not validate")
        msg: str = Field(description="explanation for why the validation failed")
        type: str = Field(description="the type of error encountered during validation")
        ctx: object = Field(description="the context of the error")

    __root__: list[BadRequestSchemaElement]


class InternalServerErrorSchema(BaseModel):
    title: str = Field(
        default="500 Internal Server Error",
        description="synonymous with the HTTP status-code of the response",
    )
    description: str = Field(
        description="explanation for why the server experienced errors"
    )
