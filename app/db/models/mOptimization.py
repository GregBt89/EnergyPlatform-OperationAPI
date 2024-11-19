from beanie import Document, BackLink, Link
from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any, Dict
from bson import ObjectId
from datetime import datetime, timezone
from app.utils.types import PydanticObjectId
from app.db.models.mShared import InputReferences
from enum import Enum


class ExecutionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OptimizationMetadata(BaseModel):
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


class OptimizationRun(Document):
    valid_from: datetime = Field(
        ..., description="Start time of the optimization horizon.")
    valid_until: datetime = Field(
        ..., description="End time of the optimization horizon.")
    metadata: OptimizationMetadata = Field(
        ..., description="Optimization metadata.")

    # Backlink to reference all associated schedules
    # asset_schedules: Optional[List[BackLink["AssetOptimizationSchedule"]]] = Field(
    #    default_factory=list, description="Backlink to associated asset schedules."
    # )

    class Settings:
        collection = "optimization_runs"
        indexes = [
            [("valid_from", 1)],
            [("metadata.status", 1)],
        ]

    @classmethod
    async def exists(clc, _id: PydanticObjectId) -> bool:
        if await clc.find_one({"_id": ObjectId(_id)}):
            return True
        return False


class Schedule(BaseModel):

    class TimePoints(BaseModel):
        timestamp: datetime = Field(
            ..., description="Timestamp of the schedule entry.")
        value: float = Field(
            ..., description="Setpoint value.")
        direction: Optional[Literal["up", "down"]] = Field(
            None, description="For frr, indicating whether to setpoint is for upwards or downwards change.")

    results_type: Literal["setpoints", "fiancial_metric", "behavior_metric", "sharing_keys"] = Field(
        "setpoints", description="The type of the results for example setpoints or the expected behaviour of the asset following the setpoints (e.g. SoC)")
    variable: str = Field(
        ..., description="The name of the variable the schedule is representing.", example="activePower")
    unit: str = Field(
        ..., description="The unit tha the variable is expressed to.", example="kW")
    values: List[TimePoints] = Field(
        ..., description="The resulted values, with timestamps", example=[{
            "timestamp": datetime.now(timezone.utc),
            "value": 50
        }]
    )


class AssetSchedule(BaseModel):
    service: Literal["arbitrage", "mfrr", "afrr"] = Field(
        "arbitrage", description="The schedule type to distinguish between different services")
    scope: Literal["day-ahead", "intra-day"] = Field(
        "day-ahead", description="The scope refers to whether results are about day-ahead or intraday")
    results: List[Schedule] = Field(
        ..., description="A list of setpoints or metrics.")


class AssetOptimizationSchedule(Document):
    asset_id: PydanticObjectId = Field(
        ..., description="Reference to the controllable asset.")
    optimization_run_id: Link["OptimizationRun"] = Field(
        ..., description="Reference to the optimization run.")
    schedule: List[AssetSchedule] = Field(
        ..., description="Schedule for the asset.")

    class Settings:
        collection = "asset_optimization_schedules"
        indexes = [
            [("asset_id", 1)],
            [("optimization_run_id", 1)],
        ]
