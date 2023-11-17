from beanie import Document, Link
from pydantic import BaseModel, Field
import pymongo

from typing import Optional, List
import datetime
from .enums import AssetType

class AssetDetails(BaseModel):
    meter_id: int = Field(...,description="The id of the meter that the assset connects with the grid")
    user_id: int = Field(..., description="The id of the user that the asset is owned by")
    asset_type : AssetType 

class AssetsCatalog(Document):
    asset_id :int = Field(..., description="The unique identifier of the asset from the GlobalRegistry DB")
    details : AssetDetails 

    class Settings:
        collection = "assets_catalog"
        indexes = [
            pymongo.IndexModel([("asset_id", 1), ("details.meter_id", 1)], unique=True),
            pymongo.IndexModel([("details.user_id", 1)]),
            pymongo.IndexModel("asset_id", unique=True)
        ]

    @classmethod
    async def by_asset_id(cls, asset_id: int) -> Optional["AssetsCatalog"]:
        """Get an asset by its id from the SQL database."""
        return await cls.find_one(cls.asset_id == asset_id)
    
    @classmethod
    async def by_asset_type(cls, asset_type: AssetType) -> Optional["AssetsCatalog"]:
        """Get all assets by the asset type."""
        return await cls.find(cls.details.asset_type == asset_type)
    
    @classmethod
    async def by_meter(cls, meter_id: int) -> Optional["AssetsCatalog"]:
        """Get all assets by the id of the meter that they are connected to."""
        return await cls.find(cls.details.meter_id == meter_id)
    
    @classmethod
    async def by_user(cls, user_id: int) -> Optional["AssetsCatalog"]:
        """Get all assets by the id of the user that are owned by."""
        return await cls.find(cls.details.user_id == user_id)
    
    async def get_measurements(self):
        """Fetch all measurements related to this asset."""
        return await AssetMeasurements.find(AssetMeasurements.asset_id.id == self.id).to_list()

    def __str__(self) -> str:
        return f"Asset ID: {self.asset_id}, Type: {self.details}"
    
class BessSpecificMeasurements(BaseModel):
    state_of_charge: float 
    state_of_health: float 
    cell_avg_temperature: Optional[float] = Field(description='in celcius')
    dc_voltage: float = Field(..., description='in V')
    dc_ampers: float = Field(..., description='in A')

class ElySpecificMeasurements(BaseModel):
    hydrogen_demand: float = Field(..., description='in kg')
    
class TypeSpecificMeasuremetns(BaseModel):
    bess: Optional[BessSpecificMeasurements] = None
    ely : Optional[ElySpecificMeasurements] = None

class AssetMeasurements(Document):
    asset_id : Link[AssetsCatalog] = Field(..., description="Reference to the _id of the assets_catalog collection")
    timestamp : datetime.datetime
    active_power: float = Field(..., description='in kW')
    reactive_power: float = Field(..., description='in kVAr')
    voltage: float = Field(..., description='in V')
    current: float = Field(..., description='in A')
    added_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    heartbeat: int
    type_specific: Optional[TypeSpecificMeasuremetns] = None

    class Settings:
        collection = "asset_measurements"

    async def get_asset_info(self) -> AssetsCatalog:
        """Retrieve detailed information of the linked asset."""
        return await self.asset_id.fetch()

    def __str__(self) -> str:
        return f"Asset ID: {self.asset_id}, Timestamp: {self.timestamp}"
    


