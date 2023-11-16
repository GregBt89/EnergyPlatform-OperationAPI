from fastapi import APIRouter, status
from ..schemas.assets import AssetCatalogIn
from ..db.models import AssetsCatalog

router = APIRouter()#, prefix="/assets")

@router.post("/assets", status_code=status.HTTP_201_CREATED)
async def add_asset_in_operations_catalog(asset_in:AssetCatalogIn):
    asset_id = asset_in.asset_id
    additional = {"meter_id":asset_in.additional.meter_id, "asset_type":asset_in.additional.asset_type}
    asset = AssetsCatalog(asset_id=asset_id, details=additional)
    await asset.create()
    return asset


