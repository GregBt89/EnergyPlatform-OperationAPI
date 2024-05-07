from pydantic import BaseModel, Field
from ..db.enums import AssetType, MeterType, PODType, ECType
from typing import Optional, Dict, List
import datetime

class Meter(BaseModel):
    meter_id: int
    meter_type: MeterType

    class Config:
        orm_mode = True

class PODBase(BaseModel):
    pod_id: int
    pod_type: PODType

    class Config:
        orm_mode = True

class MeterAndPODs(Meter):
    pods: List[PODBase]

class MetersAndPODs(BaseModel):
    meters: List[MeterAndPODs]

    class Config:
        orm_mode = True

'''
class Meter(BaseModel):
    meter_id: int
    meter_type: MeterType
'''

class POD(PODBase):
    meter_id: int

class PODMeasurements(BaseModel):
    pod_id: int
    timestamp: datetime.datetime
    energy_kwh: float

class Member(BaseModel):
    class Parameters(BaseModel):
        sharing_key_priority:Optional[int]=None
        sharing_key_percentage:Optional[float] = Field(ge=0, le=100)
        disable_proportional: Optional[bool]=None
        unit_sell_euro_kwh:Optional[float]=None

    pod_id: int
    member_type: PODType
    parameters: Parameters
    timestamp: datetime.datetime

class Members(BaseModel):
    ec_id: int
    members: List[Member]

class EC(Members):
    ec_model_id: int

class AssetCatalog(BaseModel):
    asset_type: AssetType
    asset_id: int
    meter_id: int

'''
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
'''







