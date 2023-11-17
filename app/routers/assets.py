from fastapi import APIRouter, status, HTTPException
from ..schemas.assets import AssetCatalogIn, AssetMeasurementsIn, BessMeasurementsIn, ElyMeasurementsIn
from ..db.models import AssetsCatalog, AssetMeasurements
import bson

router = APIRouter(tags=["Assets"], prefix="/assets")

@router.post("", status_code=status.HTTP_201_CREATED, tags=["Catalog"])
async def add_asset_in_operations_catalog(asset_in:AssetCatalogIn):
    asset = AssetsCatalog(**asset_in.model_dump())
    await asset.create()
    return asset

@router.post("/measurements/bess", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_bess_asset_measurements(measurements:BessMeasurementsIn):
    if not await AssetsCatalog.get(measurements.asset_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    asset_measurements = AssetMeasurements(**measurements.model_dump())
    await asset_measurements.insert()
    return asset_measurements

@router.post("/measurements/ely", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
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
async def get_measurements(asset_id:int):
    asset = await AssetsCatalog.by_asset_id(asset_id)
    if not asset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await asset.get_measurements()
    #AssetMeasurements.asset_id.id == asset.id,fetch_links=True).to_list()
    #return await asset.get_measurements()

'''@router.post("/measurements/ely", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_ely_measurements(measurements:ElyAssetMeasurementsIn):
    asset_measurements = AssetElyMeasurements(**measurements.model_dump())
    await asset_measurements.insert()
    return asset_measurements'''

'''

@router.post("/measurements", status_code=status.HTTP_201_CREATED, tags=["Measurements"])
async def inject_general_asset_measurements(measurements:AssetMeasurementsIn):
    asset_measurements = AssetElyMeasurements(**measurements.model_dump())
    await asset_measurements.insert()
    return asset_measurements
'''


