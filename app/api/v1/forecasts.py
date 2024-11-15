from fastapi import APIRouter, status, HTTPException, Depends
from typing import List, Optional, Tuple, Union
from datetime import datetime, date
from loguru import logger
from ...services import ForecastServices as FS, get_forecast_services as gfs
from ...schemas.forecasts import Forecasts

router = APIRouter(tags=["Forecasts"], prefix="/forecasts")


@router.post("/assets/{asset_id}")
async def add_new_asset_forecasts(asset_id:str, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_asset_forecasts(asset_id, forecast)
