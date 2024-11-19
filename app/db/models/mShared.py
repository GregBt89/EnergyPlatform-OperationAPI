from typing import Optional, List
from pydantic import BaseModel, Field
from app.utils.types import PydanticObjectId


class InputReferences(BaseModel):
    database_name: Optional[str] = Field(
        None, description="""
        The name of the database that the collection belongs to.
        If none the current db will be assumed
        """
    )
    collection_name: str = Field(
        ..., description="The name of the collection the inputs belong to")
    input_refs: List[PydanticObjectId] = Field(
        default_factory=list,  description="""
        The list of _id for the inputs used from the colleciton to make the forecast/optimization
        """
    )
