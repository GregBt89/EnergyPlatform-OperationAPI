from pydantic import BaseModel, Field
from ..db.enums import AssetType, MeterType, PODType, ECType
from typing import Optional, List
import datetime
from bson import ObjectId


class BaseORM(BaseModel):
    class Config:
        from_attributes = True


class Meter(BaseORM):
    meter_id: int
    meter_alias: Optional[str] = None
    meter_type: MeterType


class PODBase(BaseORM):
    pod_id: int
    pod_type: PODType


class MeterAndPODs(Meter):
    pods: List[PODBase]


class MetersAndPODs(BaseORM):
    meters: List[MeterAndPODs]


'''
class Meter(BaseModel):
    meter_id: int
    meter_type: MeterType
'''


class POD(PODBase):
    meter_id: int
    _meter_mongo_id: Optional[ObjectId] = None

    def set_meter_mongo_id(self, value: ObjectId):
        self._meter_mongo_id = value

    def get_meter_mongo_id(self) -> ObjectId:
        return self._meter_mongo_id


class PODMeasurements(BaseModel):
    pod_id: int
    timestamp: datetime.datetime
    energy_kwh: float


class Member(BaseModel):

    pod_id: int
    pod_type: PODType
    sharing_key_priority: Optional[int] = None
    sharing_key_percentage: Optional[float] = Field(ge=0, le=100)
    disable_proportional: Optional[bool] = None
    unit_sell_euro_kwh: Optional[float] = None
    timestamp: Optional[datetime.datetime] = datetime.datetime.now(
        datetime.timezone.utc)

    _pod_mongo_id: Optional[ObjectId] = None

    def set_pod_mongo_id(self, value: ObjectId):
        self._pod_mongo_id = value

    def get_pod_mongo_id(self) -> ObjectId:
        return self._pod_mongo_id


class EC(Member):
    ec_id: int

    # _ec_mongo_id: Optional[ObjectId]=None

    # def set_ec_mongo_id(self, value: ObjectId):
    #    self._ec_mongo_id = value

    # def get_ec_mongo_id(self) -> ObjectId:
    #    return self._ec_mongo_id


class AssetCatalog(BaseModel):
    asset_type: AssetType
    asset_id: int
    meter_id: int
    _meter_mongo_id: Optional[ObjectId] = None

    def set_meter_mongo_id(self, value: ObjectId):
        self._meter_mongo_id = value

    def get_meter_mongo_id(self) -> ObjectId:
        return self._meter_mongo_id


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
