from typing import (
    Annotated,
    Union,
    List,
    Dict,
    Callable,
    Any,
    Tuple,
    TypeVar,
    Generic,
    Optional
)
from beanie import Link
from pydantic_core import core_schema
from bson import ObjectId
from datetime import datetime, date
from loguru import logger

from fastapi import Query

T = TypeVar("T")  # Generic type for the document type linked to


class _LinkTypeAnnotation(Generic[T]):
    """
    Custom Pydantic annotation for LinkType to handle schema validation and serialization.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> Link:
            """
            Validate a string representation of the ObjectId and return a Link object.
            """
            if not ObjectId.is_valid(input_value):
                raise ValueError(f"Invalid ObjectId: {input_value}")
            # Return a Link with the given ObjectId
            return Link[T](id=ObjectId(input_value))

        return core_schema.union_schema(
            [
                # Check if it's already a Link
                core_schema.is_instance_schema(Link),
                core_schema.no_info_plain_validator_function(
                    validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


LinkType = Annotated[Link[T], _LinkTypeAnnotation]


class _ObjectIdPydanticAnnotation:
    # Based on https://docs.pydantic.dev/latest/usage/types/custom/#handling-third-party-types.

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        def validate_from_str(input_value: str) -> ObjectId:
            return ObjectId(input_value)

        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(
                    validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )


PydanticObjectId = Annotated[
    str, _ObjectIdPydanticAnnotation
]


ID = Union[int, PydanticObjectId]

POD_ID = ID
ASSET_ID = Annotated[ID, Query(description="An integer or a valid MongoDB ObjectId")]

DATEOPTIONS = Union[datetime, date, None]
DATERANGE = Tuple[DATEOPTIONS, DATEOPTIONS]
