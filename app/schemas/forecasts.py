from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Any, List, Union, Literal
from beanie import PydanticObjectId
from bson import ObjectId

from ..db.models.forecasts import (
    ForecastMetadata, 
    ForecastValue, 
    InputReferences,
    PydanticObjectId
)

# Base class for shared forecast structure
class Forecasts(BaseModel):
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
                PydanticObjectId("666f6f2d6261722d71757578"),
                PydanticObjectId("666f6f2d6261722d71757578")
            ],
            "parameters": {
                "confidence_interval": 95,
                "smoothing_factor": 0.5
            }
        }
    )

class AssetForecastIn(Forecasts):
    asset_id: PydanticObjectId = Field(description="Reference to Assets Catalog")


