from app.schemas.shForecasts import Forecasts
from fastapi import APIRouter, Depends, Query
from loguru import logger
from app.services import (
    ForecastServices as FS,
    get_forecast_services as gfs
)
from app.utils.types import (
    ASSET_ID,
    POD_ID,
    PydanticObjectId
)
from typing import Union, Annotated, Optional
from datetime import datetime
from pydantic import Field, BaseModel, field_validator
from bson import ObjectId

router = APIRouter(tags=["Forecasts"], prefix="/forecasts")


@router.post("/assets/{asset_id}")
async def add_new_asset_forecasts(asset_id: PydanticObjectId, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_asset_forecasts(asset_id, forecast)



class AssetForecastQuery(BaseModel):
    asset_id: Union[int, str] = Field(...,
                                description="An integer or a valid MongoDB ObjectId")
    valid_from: Optional[datetime] = Field(None,
                                description="An integer or a valid MongoDB ObjectId")
    forecast_id: Optional[PydanticObjectId] = Field(None,
                                description="An integer or a valid MongoDB ObjectId", serialization_alias="_id")

    @field_validator('asset_id')
    def validate_asset_id(cls, value, _info):
        if value.isdigit():
            return int(value)  # Convert to integer if it's numeric
        if ObjectId.is_valid(value):
            return ObjectId(value)  # Convert to ObjectId if it's valid
        raise ValueError(
            "asset_id must be either an integer or a valid ObjectId string")


@router.get("/assets")
async def get_asset_forecasts(query: AssetForecastQuery = Depends(), services: FS = Depends(gfs)):
    return await services.get_asset_forecasts(query)


@router.post("/pods/{pod_id}")
async def add_new_pod_forecasts(pod_id: PydanticObjectId, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_pod_forecasts(pod_id, forecast)


@router.get("/pods")
async def get_asset_forecasts(pod_id: POD_ID, services: FS = Depends(gfs)):
    return await services.get_asset_forecasts(pod_id)
