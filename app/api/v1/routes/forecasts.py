from app.validation.schemas.shForecasts import Forecasts
from fastapi import APIRouter, Depends, Query
from loguru import logger
from app.services import (
    ForecastServices as FS,
    get_forecast_services as gfs
)
from app.validation.queries.vqForecasts import AssetForecastsQuery
from app.utils.types import (
    ASSET_ID,
    POD_ID,
    PydanticObjectId
)

router = APIRouter(tags=["Forecasts"], prefix="/forecasts")


@router.post("/assets/{asset_id}")
async def add_new_asset_forecasts(asset_id: PydanticObjectId, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_asset_forecasts(asset_id, forecast)

@router.get("/assets")
async def get_asset_forecasts(query_params: AssetForecastsQuery = Depends(), services: FS = Depends(gfs)):
    return query_params
    #return await services.get_asset_forecasts(query_params)


@router.post("/pods/{pod_id}")
async def add_new_pod_forecasts(pod_id: PydanticObjectId, forecast: Forecasts, services: FS = Depends(gfs)):
    return await services.inject_pod_forecasts(pod_id, forecast)


@router.get("/pods")
async def get_asset_forecasts(pod_id: POD_ID, services: FS = Depends(gfs)):
    return await services.get_asset_forecasts(pod_id)
