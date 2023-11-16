from pydantic import BaseModel
from ..db.enums import AssetType

class AssetCatalogDetails(BaseModel):
    asset_type: AssetType
    meter_id:str

class AssetCatalogIn(BaseModel):
    asset_id : str
    additional : AssetCatalogDetails
