from typing import Union, Optional, Set
from bson import ObjectId
from dataclasses import asdict, fields
from urllib.parse import urlencode

class BaseQuery:

    def model_dump(self,
                   exclude_none: bool = False,
                   exclude: Optional[Set[str]] = None,
                   as_query_string: bool = False
                   ) -> dict:
        """Convert dataclass to dictionary, dynamically applying serialization aliases."""
        exclude = exclude or set()
        data = asdict(self)
        result = {}

        # Dynamically apply aliases from Query metadata
        for field_info in fields(self):
            field_name = field_info.name
            value = data[field_name]

            # Skip fields that are excluded
            if field_name in exclude:
                continue

            # Get the Query object and its alias (if any)
            query_obj = field_info.default
            alias = getattr(query_obj, "serialization_alias", None)

            # Use the alias if available; otherwise, use the field name
            key = alias if alias else field_name

            if not (exclude_none and value is None):  # Exclude None if requested
                result[key] = value

        # Return as query string if requested
        return urlencode(result) if as_query_string else result
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
