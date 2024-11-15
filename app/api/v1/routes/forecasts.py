from app.schemas.shForecasts import Forecasts
from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional, Tuple, Union
from datetime import datetime, date
from loguru import logger
from app.services import (
    ForecastServices as FS,
    get_forecast_services as gfs
)
from app.db.models.mForecasts import PydanticObjectId
from app import (ASSET_ID)



router = APIRouter(tags=["Forecasts"], prefix="/forecasts")


@router.post("/assets/{asset_id}")
async def add_new_asset_forecasts(asset_id: str, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_asset_forecasts(asset_id, forecast)


@router.get("/assets")
async def get_asset_forecasts(services: FS = Depends(gfs)):
    return await services.get_asset_forecasts()


@router.post("/pods/{pod_id}")
async def add_new_pod_forecasts(asset_id: str, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_asset_forecasts(asset_id, forecast)


@router.get("/pods")
async def get_asset_forecasts(pod_id: POD, services: FS = Depends(gfs)):
    return await services.get_asset_forecasts(pod_id)
