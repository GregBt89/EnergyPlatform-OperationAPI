from beanie import Document
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict, Union
from bson import ObjectId
from datetime import datetime, timezone
from app.utils.types import PydanticObjectId
from app.db.models.mShared import InputReferences
from enum import Enum
from app.schemas import FromAttributes


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationMetadata(FromAttributes):
    o_model_name: str = Field(
        ..., description="Optimization model name.", example="MILP-DayAhead-VPP")
    o_model_version: str = Field(
        ..., description="Optimization model version.", example="milpDaVpp_v1")
    executed_at: datetime = Field(
        ..., description="Execution timestamp.", example=datetime.now(timezone.utc))
    status: ExecutionStatus = Field(
        ExecutionStatus.RUNNING, description="Indicates the optimization run status")
    added_at: datetime = Field(
        ..., description="Time when was added in the collection.", example=datetime.now(timezone.utc))
    schema_version: int = Field(1, description="Schema version.")
    input_references: List[InputReferences] = Field(
        ..., description="References to input documents.",
        example=[{"database_name": "historicalDb",
                  "collection_name": "historicalAssets",
                  "input_refs": [
                      PydanticObjectId(
                          "666f6f2d6261722d71757578"),
                      PydanticObjectId(
                          "666f6f2d6261722d71757578")
                  ]}])
    # Placeholder for optimization parameters. SHould be revised, (asset paremetners, constraints?)
    parameters: Optional[Dict[str, Any]] = Field(
        None, description="Optimization parameters.",
        example={
            "confidence_interval": 95,
            "smoothing_factor": 0.5
        })

    class Config:
        from_attributes = True


class OptimizationRun(Document):
    valid_from: datetime = Field(
        ..., description="Start time of the optimization horizon.")
    valid_until: datetime = Field(
        ..., description="End time of the optimization horizon.")
    metadata: Optional[OptimizationMetadata] = Field(
        None, description="Optimization metadata.")

    # Backlink to reference all associated schedules
    asset_schedules: Optional[List[PydanticObjectId]] = Field(
        default_factory=list,
        description="Backlink to associated asset schedules."
    )

    class Settings:
        collection = "optimization_runs"
        indexes = [
            [("valid_from", 1)],
            [("metadata.status", 1)],
        ]

    @classmethod
    async def exists(clc, _id: ObjectId, links=False) -> Union["OptimizationRun", False]:
        run = await clc.find_one(
            {"_id": ObjectId(_id)},
            fetch_links=links
        )
        if run:
            return run
        return False


class Schedule(BaseModel):

    results_type: Literal["setpoints", "reserve", "metrics", "sharing_keys"] = Field(
        "setpoints", description="The type of the results for example setpoints or the expected behaviour of the asset following the setpoints (e.g. SoC)")
    variable: str = Field(
        ..., description="The name of the variable the schedule is representing.", example="activePower")
    unit: str = Field(
        ..., description="The unit tha the variable is expressed to.", example="kW")
    values: List = Field(
        ..., default_factory=list,
        description="The resulted values", example=[50, 55, 55, 61, 23, 63]
    )

    class Config:
        from_attributes = True


class AssetSchedule(BaseModel):
    service: Literal["arbitrage", "mfrr", "afrr"] = Field(
        "arbitrage", description="The schedule type to distinguish between different services")
    scope: Literal["day-ahead", "intra-day"] = Field(
        "day-ahead", description="The scope refers to whether results are about day-ahead or intraday")
    schedule: List[Schedule] = Field(
        ..., description="A list of setpoints or metrics.")

    class Config:
        from_attributes = True


class AssetOptimizationSchedule(Document):
    asset_id: PydanticObjectId = Field(
        ..., description="Reference to the controllable asset.")
    optimization_run_id: PydanticObjectId = Field(
        ..., description="Reference to the optimization run.")
    timestamp: List[datetime] = Field(
        ..., description="Timestamps of the results.")
    results: List[AssetSchedule] = Field(
        ..., description="Schedule for the asset.")

    class Settings:
        collection = "asset_optimization_schedules"
        indexes = [
            [("asset_id", 1)],
            [("optimization_run_id", 1)],
        ]

    @classmethod
    async def exists(clc, asset_id: ObjectId, run_id: Optional[ObjectId] = None, links=False) -> Optional[List["AssetOptimizationSchedule"]]:
        query = {
            "asset_id": ObjectId(asset_id)
        }
        if run_id:
            query.update(
                {
                    "optimization_run_id": {
                        '$ref': "OptimizationRun",
                        '$id': ObjectId(run_id)
                    }
                }
            )

        return await clc.find(
            query,
            fetch_links=links
        ).to_list()

    @ classmethod
    async def by_optimization_run_id(cls, run_id: ObjectId) -> List["AssetOptimizationSchedule"]:
        """
        Fetch all AssetOptimizationSchedule documents associated with the given optimization run ID.

        Args:
            run_id (ObjectId): The ID of the optimization run.

        Returns:
            List[AssetOptimizationSchedule]: A list of matching schedules.
        """
        query = {
            "optimization_run_id": {
                "$ref": "OptimizationRun",
                "$id": run_id
            }
        }

        return await cls.find(query).to_list()
