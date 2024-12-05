from pydantic import BaseModel, Field, field_serializer
from beanie import Link
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from loguru import logger
from app.utils.types import PydanticObjectId, LinkType
from app.db.models.mOptimization import (
    OptimizationMetadata,
    AssetSchedule
)
from app.validation.schemas import FromAttributes


class OptimizationRun(FromAttributes):
    valid_from: datetime = Field(
        ..., description="Start time of the optimization horizon.")
    valid_until: datetime = Field(
        ..., description="End time of the optimization horizon.")
    metadata: Optional[OptimizationMetadata] = Field(
        None, description="For now we set metadata to an optional attribute")


class OptimizationRunResponse(OptimizationRun):
    run_id: PydanticObjectId = Field(..., alias="run_id")


class AssetOptimizationResults(FromAttributes):
    asset_id: PydanticObjectId = Field(
        ..., description="The id of the asset that the results refer to.", example=str(ObjectId()))
    timestamp: List[datetime] = Field(
        ..., description="Timestamps of the results.")
    results: List[AssetSchedule] = Field(
        ..., default_factory=list, description="Schedule for the asset.")


class AssetOptimizationResultsResponse(FromAttributes):
    asset_id: PydanticObjectId = Field(
        ..., description="The id of the asset that the results refer to.", example=str(ObjectId()))
    schedule: List[AssetSchedule] = Field(
        ..., description="Schedule for the asset.")
    optimization_run_id: LinkType = Field(
        ..., description="the optimization run that the results belong to.")

    @field_serializer('optimization_run_id')
    def serialize_optimization_run_id(self, optimization_run_id: LinkType, _info):
        return str(optimization_run_id.ref.id)


class OptimizationRuResultsResponse(OptimizationRun):
    asset_schedules: Optional[List["AssetOptimizationResults"]] = Field(
        None, description="A list of schedules corresponsing to asset optimization results")
    id: PydanticObjectId = Field(
        ..., serialization_alias="run_id", alias="_id", description="The run id grouping the asset_schedules under the same optimization task.")
