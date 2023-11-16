from beanie import Document, Link, Indexed
from pydantic import BaseModel, Field

from typing import Optional, List
import datetime
from .enums import AssetType

class AssetDetails(BaseModel):
    meter_id: Indexed(str, unique=True) = Field(...,description="The id of the meter that the assset connects with the grid")
    asset_type : AssetType = Field(..., description="The type of the asset")

class AssetsCatalog(Document):
    asset_id : Indexed(str, unique=True) = Field(..., description="The unique identifier of the asset from the GlobalRegistry DB")
    details : AssetDetails 

    class Settings:
        collection = "assets_catalog"

    async def get_measurements(self):
        """Fetch all measurements related to this asset."""
        return await AssetMeasurements.find(AssetMeasurements.asset_id == self.asset_id).to_list()

    def __str__(self) -> str:
        return f"Asset ID: {self.asset_id}, Type: {self.asset_type}"

class AssetMeasurements(Document):
    asset_id : Link[AssetsCatalog] = Field(..., description="Reference to the asset_id of the assets_catalog collection")
    timestamp : datetime.datetime = Field(...)
    active_power: float = Field(..., description='in kW')
    reactive_power: float = Field(..., description='in kVAr')
    voltage: float = Field(..., description='in V')
    current: float = Field(..., description='in A')
    added_at: datetime.datetime = Field(default_factory=datetime.datetime.now)

    class Settings:
        collection = "asset_measurements"

    async def get_asset_info(self) -> AssetsCatalog:
        """Retrieve detailed information of the linked asset."""
        return await self.asset_id.fetch()

    def __str__(self) -> str:
        return f"Asset ID: {self.asset_id}, Timestamp: {self.timestamp}"
    
class BessSpecificMeasurements(BaseModel):
    state_of_charge: float = Field(..., description='in percentage')
    state_of_health: float = Field(..., description='in percentage')
    cell_avg_temperature: Optional[float] = Field(description='in celcius')
    dc_voltage: float = Field(..., description='in V')
    dc_ampers: float = Field(..., description='in A')
    
class AssetBessMeasurements(AssetMeasurements):
    type_specific: BessSpecificMeasurements