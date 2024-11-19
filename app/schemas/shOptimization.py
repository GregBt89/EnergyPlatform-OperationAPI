from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.utils.types import PydanticObjectId
from app.db.models.mOptimization import (
    OptimizationMetadata,
    AssetSchedule
)


class OptimizationRun(BaseModel):
    valid_from: datetime = Field(
        ..., description="Start time of the optimization horizon.")
    valid_until: datetime = Field(
        ..., description="End time of the optimization horizon.")
    metadata: Optional[OptimizationMetadata] = Field(
        None, description="For now we set metadata to an optional attribute")

    class Config:
        from_attributes = True


class OptimizationRunResponse(OptimizationRun):
    run_id: PydanticObjectId = Field(..., alias="optimization_run_id")

    class Config:
        from_attributes = True


class AssetOptimizationResults(BaseModel):
    asset_id: PydanticObjectId = Field(
        ..., description="The id of the asset that the results refer to.", example=str(ObjectId()))
    schedule: List[AssetSchedule] = Field(
        ..., description="Schedule for the asset.")

    class Config:
        from_attributes = True


class AssetOptimizationResultsResponse(OptimizationRun):
    asset_schedules: Optional[List["AssetOptimizationResults"]] = None
    id: PydanticObjectId = Field(..., serialization_alias="run_id")

    class Config:
        from_attributes = True