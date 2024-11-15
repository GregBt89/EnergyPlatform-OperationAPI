from beanie import Document, Indexed, Link, Insert, before_event
from pydantic_core import core_schema
from bson import ObjectId
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Callable, Annotated
from datetime import datetime, timezone
from loguru import logger
from .catalogs import AssetsCatalog, PODCatalog

# Define a custom type for ObjectId compatibility
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
                core_schema.no_info_plain_validator_function(validate_from_str),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

PydanticObjectId = Annotated[
    str, _ObjectIdPydanticAnnotation
]



class InputReferences(BaseModel):
    database_name: Optional[str] = Field(
        None, description="The name of the database that the collection belongs to. If none the current db will be assumed")
    collection_name: str = Field(
        ..., description="The name of the collection the inputs belong to")
    input_refs: List[PydanticObjectId] = Field(
        default_factory=list,  description="The list of _id for the inputs used from the colleciton to make the forecast")


class ForecastMetadata(BaseModel):
    added_at: datetime = Field(...,
                               description="Timestamp when the forecast was added in the database")
    executed_at: datetime = Field(...,
                                  description="Timestamp when the forecat was executed")
    schema_version: int = Field(...,
                                description="The version of the Forecast Schema")
    model_id: int = Field(..., description="the id of the forecast model")
    model_name: Optional[str] = Field(None, description="The model name")
    input_references: List[InputReferences] = Field(
        ..., description="A list of input references to other collection that were used to make the forecasts.")
    parameters: Optional[Any] = Field(
        None, description="Possible parameters that are passed in the forecast model")

# Define the schema for each individual forecast value


class ForecastValue(BaseModel):
    timestamp: datetime = Field(...,
                                description="Timestamp of the forecasted value")
    value: float = Field(...,
                         description="Forecasted value at the specified timestamp")


# Base class for shared forecast structure
class BaseForecast(Document):
    # Common fields across all forecast types
    forecast_type: Literal["demand", "production", "weather",
                           "market"] = Field(..., description="Type of forecast")
    granularity: Literal["15min", "1h"] = Field(
        ..., description="Granularity of forecast values (e.g., 15 minutes or 1 hour)")
    valid_from: datetime = Field(...,
                                 description="Start time of the forecast period")
    valid_until: datetime = Field(...,
                                  description="End time of the forecast period")

    # Array of forecasted values with timestamps
    forecast_values: List[ForecastValue] = Field(
        ..., description="List of forecasted values with timestamps")

    # Metadata with schema version and model details
    metadata: ForecastMetadata = Field(
        ...,
        description="Metadata about the forecast, including model details, schema version, and parameters",
        example={
            "added_at": datetime.now(timezone.utc),
            "schema_version": 1,
            "model_name": "Neural Network",
            "model_id": "NN_v3.2",
            "executed_at": datetime.now(timezone.utc),
            "input_references": [
                ObjectId("666f6f2d6261722d71757578"),
                ObjectId("666f6f2d6261722d71757578")
            ],
            "parameters": {
                "confidence_interval": 95,
                "smoothing_factor": 0.5
            }
        }
    )

class AssetForecast(BaseForecast):
    asset_id: PydanticObjectId = Field(
        ..., description="Reference to the Asset catalog entry, if passed asset_id doesnt exist an error will be raised")

    class Settings:
        collection = "asset_forecasts"
        # Indexes that are common across all forecast types
        indexes = [
            # Index for retrieving forecasts by time range
            [
                ("asset_id", 1),
                ("valid_from", 1),
                ("valid_until", 1)
            ],
            # Index on generation_timestamp for retrieving the latest forecast
            "added_at"
        ]

    @before_event(Insert)
    async def validate_asset_id_exists(self):
        # Check if the asset_id exists in the AssetsCatalog collection
        exists = await AssetsCatalog.find_one({"_id": self.asset_id})
        if not exists:
            raise ValueError(
                f"Referenced asset_id {self.asset_id} does not exist in AssetsCatalog.")


class PodForecast(BaseForecast):
    pod_id: PydanticObjectId = Field(
        ..., description="Reference to the POD catalog entry, if passed pod_id doesnt exist an error will be raised")

    class Settings:
        collection = "pod_forecasts"
        # Indexes that are common across all forecast types
        indexes = [
            # Index for retrieving forecasts by time range
            [
                ("pod_id", 1),
                ("valid_from", 1),
                ("valid_until", 1)
            ],
            # Index on generation_timestamp for retrieving the latest forecast
            "added_at"
        ]

    @before_event(Insert)
    async def validate_pod_id_exists(self):
        # Check if the asset_id exists in the AssetsCatalog collection
        exists = await AssetsCatalog.find_one({"_id": self.pod_id})
        if not exists:
            raise ValueError(
                f"Referenced pod_id {self.pod_id} does not exist in AssetsCatalog.")


class MarketForecast(BaseForecast):
    market_id : PydanticObjectId = Field(description="Reference to market id from market catalog")

    class Settings:
        collection = "pod_forecasts"
        # Indexes that are common across all forecast types
        indexes = [
            # Index for retrieving forecasts by time range
            [
                ("pod_id", 1),
                ("valid_from", 1),
                ("valid_until", 1)
            ],
            # Index on generation_timestamp for retrieving the latest forecast
            "added_at"
        ]
