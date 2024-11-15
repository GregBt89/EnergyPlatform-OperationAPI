from fastapi import APIRouter, Depends
from typing import List

from app.schemas.shCatalogs import *
from app.services import (
    CatalogServices,
    get_catalog_services as gcs
)

router = APIRouter(tags=["Catalogs"], prefix="/catalogs")


@router.post("/meters")
async def add_new_meters(new_meters: List[Meter],
                         catalog_services: CatalogServices = Depends(gcs)) -> None:
    return await catalog_services.add_meters(new_meters)


@router.get("/meters/{meter_id:int}")
async def get_pods_of_meter(meter_id: int,
                            catalog_services: CatalogServices = Depends(gcs)):
    return await catalog_services.get_meter(meter_id)


@router.post("/pods")
async def add_new_pods(new_pods: List[POD],
                       catalog_services: CatalogServices = Depends(gcs)):
    return await catalog_services.add_pods_in_catalog(new_pods)


@router.get("/pods")
async def get_pods(catalog_services: CatalogServices = Depends(gcs)):
    return await catalog_services.get_all_pods()


@router.post("/ec")
async def add_new_ec(new_ec: List[EC],
                     catalog_services: CatalogServices = Depends(gcs)):
    return await catalog_services.add_ec_member_parameters_in_catalogs(new_ec)

'''
@router.post("/ec/members")
async def add_new_ec_members(members: schemas.Members,
                        catalog_services:CatalogServices = Depends(get_catalog_services)):
    return await catalog_services.add_ec_member_parameters_in_catalogs(members)
'''


@router.post("/assets")
async def add_new_asset(assets: List[AssetCatalog],
                        catalog_services: CatalogServices = Depends(gcs)):
    return await catalog_services.add_asset_ids_in_catalogs(assets)


@router.get("/assets")
async def get_all_assets(catalog_services: CatalogServices = Depends(gcs)):
    return await catalog_services.get_all_assets()
