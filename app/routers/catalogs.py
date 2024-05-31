from fastapi import APIRouter, status, HTTPException, Depends
from motor import motor_asyncio
from ..internal import schemas
from ..db.models import MeterCatalog, PODCatalog, ECCatalog, ECMembersCatalog, AssetsCatalog
from typing import List
from .services.catalog_services import CatalogServices
from ..db.config import get_client
router = APIRouter(tags=["Catalogs"], prefix="/catalogs")

async def get_catalog_services(client:motor_asyncio.AsyncIOMotorClient = Depends(get_client)) -> CatalogServices:
    return CatalogServices(client)

@router.post("/meters")
async def add_new_meter(new_meters: schemas.MetersAndPODs,
                        catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.add_meter_and_pod_ids_in_catalogs(new_meters)

@router.get("/meters/{meter_id:int}")
async def get_pods_of_meter(meter_id:int,
                        catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.get_meter(meter_id)

@router.post("/pods")
async def add_new_pod(new_pods: List[schemas.POD],
                      catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.add_pod_ids_in_catalogs(new_pods)

@router.get("/pods")
async def get_pods(catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.get_all_pods()

@router.post("/ec")
async def add_new_ec(new_ec: schemas.EC,
                     catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.add_ec_id_in_catalogs(new_ec)

@router.post("/ec/members")
async def add_new_ec_members(members: schemas.Members,
                        catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.add_ec_member_parameters_in_catalogs(members)

@router.post("/assets")
async def add_new_asset(assets: List[schemas.AssetCatalog],
                        catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.add_asset_ids_in_catalogs(assets)
    

    





