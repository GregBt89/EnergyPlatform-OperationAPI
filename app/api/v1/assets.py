from fastapi import APIRouter, status, HTTPException, Depends
from ...schemas.measurements import BessMeasurementsIn, AssetMeasurementsIn, MeasurementsOut
from ...services import MeasurementServices as MS, get_measurement_services as gms
from typing import List, Optional, Tuple, Union
from datetime import datetime, date
from loguru import logger

router = APIRouter(tags=["Assets"], prefix="/assets")

DATEOPTIONS = Union[datetime, date, None]
DATERANGE = Tuple[DATEOPTIONS, DATEOPTIONS]


@router.get("/measurements/bess", response_model=MeasurementsOut, response_model_exclude_none=True)
async def get_bess_measurements(asset_id: Union[str, int] = None,
                                asset_mongo_id: Optional[str] = None,
                                start_date: Optional[DATEOPTIONS] = None,
                                end_date: Optional[DATEOPTIONS] = None,
                                services: MS = Depends(gms)):
    return await services.get_bess_measurements(
        asset_id, asset_mongo_id=asset_mongo_id, start_date=start_date, end_date=end_date
    )


@router.get("/measurements/pvpp", response_model=MeasurementsOut, response_model_exclude_none=True)
async def get_pvpp_measurements(asset_id: Optional[str] = None,
                                asset_mongo_id: Optional[str] = None,
                                start_date: Optional[DATEOPTIONS] = None,
                                end_date: Optional[DATEOPTIONS] = None,
                                services: MS = Depends(gms)):
    return await services.get_pvpp_measurements(
        asset_id, asset_mongo_id=asset_mongo_id, start_date=start_date, end_date=end_date
    )


@router.get("/measurements/wpp", response_model=MeasurementsOut, response_model_exclude_none=True)
async def get_wpp_measurements(asset_id: Optional[str] = None,
                               asset_mongo_id: Optional[str] = None,
                               start_date: Optional[DATEOPTIONS] = None,
                               end_date: Optional[DATEOPTIONS] = None,
                               services: MS = Depends(gms)):
    try:
        return await services.get_wpp_measurements(
            asset_id, asset_mongo_id=asset_mongo_id, start_date=start_date, end_date=end_date
        )
    except Exception as e:
        logger.debug(e)


@router.get("/measurements/hydro", response_model=MeasurementsOut, response_model_exclude_none=True)
async def get_hpp_measurements(asset_id: Optional[str] = None,
                               asset_mongo_id: Optional[str] = None,
                               start_date: Optional[DATEOPTIONS] = None,
                               end_date: Optional[DATEOPTIONS] = None,
                               services: MS = Depends(gms)):
    return await services.get_hpp_measurements(
        asset_id, asset_mongo_id=asset_mongo_id, start_date=start_date, end_date=end_date
    )


@router.post("/measurements/bess", status_code=status.HTTP_201_CREATED)
async def inject_bess_measurements(measurements: List[BessMeasurementsIn], services: MS = Depends(gms)):
    return await services.inject_bess_measurements(measurements)


@router.post("/measurements/pvpp", status_code=status.HTTP_201_CREATED)
async def inject_pvpp_measurements(measurements: List[AssetMeasurementsIn], services: MS = Depends(gms)):
    return await services.inject_pvpp_measurements(measurements)


@router.post("/measurements/wpp", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_wpp_measurements(measurements: List[AssetMeasurementsIn], services: MS = Depends(gms)):
    return await services.inject_wpp_measurements(measurements)


@router.post("/measurements/hydro", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_hydro_measurements(measurements: List[AssetMeasurementsIn], services: MS = Depends(gms)):
    return await services.inject_hydro_measurements(measurements)


'''@router.post("/measurements/ely", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_ely_asset_measurements(measurements:ElyMeasurementsIn):
    if not await AssetsCatalog.get(measurements.asset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    asset_measurements = AssetMeasurements(**measurements.model_dump())
    await asset_measurements.insert()
    return asset_measurements

@router.post("/measurements", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_asset_measurements(measurements:AssetMeasurements):
    if not await AssetsCatalog.get(measurements.asset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    asset_measurements = AssetMeasurements(**measurements.model_dump())
    await asset_measurements.insert()
    return asset_measurements

@router.get("/measurements/{asset_id:int}", status_code=status.HTTP_200_OK, tags=["Measurements"])
async def get_measurements_of_asset(asset_id:int):
    asset = await AssetsCatalog.by_asset_id(asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await asset.get_measurements()'''
