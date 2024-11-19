from typing import (
    Annotated,
    Union,
    List,
    Dict,
    Callable,
    Any,
    Tuple
)
from pydantic_core import core_schema
from bson import ObjectId
from datetime import datetime, date


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
ASSET_ID = ID

DATEOPTIONS = Union[datetime, date, None]
DATERANGE = Tuple[DATEOPTIONS, DATEOPTIONS]
