from pydantic import BaseModel
from ..db.enums import AssetType
from typing import Optional, Dict
import datetime


class AssetCatalogDetails(BaseModel):
    asset_type: AssetType
    user_id: int
    meter_id:int

class AssetCatalogIn(BaseModel):
    asset_id : int
    details : AssetCatalogDetails

class BessSpecific(BaseModel):
    state_of_charge: float 
    state_of_health: float 
    cell_avg_temperature: Optional[float] 
    dc_voltage: float 
    dc_ampers: float 

class BESS(BaseModel):
    bess: BessSpecific

class ElySpecific(BaseModel):
    hydrogen_demand:float

class ELY(BaseModel):
    ely: ElySpecific

class AssetMeasurementsIn(BaseModel):
    asset_id : str
    timestamp : datetime.datetime
    active_power: float
    reactive_power: float 
    voltage: float 
    current: float 
    heartbeat: int 

class BessMeasurementsIn(AssetMeasurementsIn):
    type_specific: BESS

class ElyMeasurementsIn(AssetMeasurementsIn):
    type_specific: ELY








