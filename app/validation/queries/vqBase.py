from typing import Union
from bson import ObjectId
from dataclasses import asdict, fields

class BaseQuery:

    def model_dump(self, exclude_none: bool = False) -> dict:
        """Convert dataclass to dictionary, dynamically applying serialization aliases."""
        data = asdict(self)
        result = {}

        # Dynamically apply aliases from Query metadata
        for field_info in fields(self):
            field_name = field_info.name
            value = data[field_name]

            # Get the Query object and its alias (if any)
            query_obj = field_info.default
            alias = getattr(query_obj, "serialization_alias", None)

            # Use the alias if available; otherwise, use the field name
            key = alias if alias else field_name

            if not (exclude_none and value is None):  # Exclude None if requested
                result[key] = value

        return result

    def _convert_to_object_id(self, field_name: str) -> ObjectId:
        value: str = getattr(self, field_name)
        if value:
            if ObjectId.is_valid(value):
                # If valid ObjectId, convert
                return ObjectId(value)
            raise ValueError(
                f"{field_name} must be a valid ObjectId string"
            )
        
    def _convert_to_integer(self, field_name:str) -> Union[int, None]:
        value: str = getattr(self, field_name)
        if value.isdigit():
            return int(value)
