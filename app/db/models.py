from beanie import Document, Link, Indexed
from pydantic import BaseModel, Field
from bson import ObjectId
from beanie.operators import In
import pymongo


from typing import Optional, List, Annotated
import datetime
from .enums import PODType, MeterType, ECType, AssetType


class MeterCatalog(Document):
    meter_id: Annotated[int, Indexed(unique=True)]
    meter_type: MeterType
    meter_alias: Optional[str] = None

    @classmethod
    async def all(cls) -> Optional["MeterCatalog"]:
        """Get an meter by its SQL id."""
        return await cls.find_all().to_list()

    @classmethod
    async def by_meter_id(cls, meter_id: int) -> Optional["MeterCatalog"]:
        """Get an meter by its SQL id."""
        query = {"meter_id": meter_id}
        return await cls.find_one(query)

    @classmethod
    async def by_ids(cls, _ids: List[ObjectId]) -> List["MeterCatalog"]:
        """Get meters by a list of MongoDB ObjectIds."""
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find({"_id": {"$in": _ids}}).to_list()

    @classmethod
    async def fetch_one_with_pods(cls, meter_id: int):
        pipeline = [
            {
                '$match': {
                    'meter_id': meter_id
                }
            }, {
                '$lookup': {
                    'from': PODCatalog.__name__,
                    'localField': '_id',
                    'foreignField': 'meter_mongo_id.$id',
                    'as': 'pods'
                }
            }, {
                '$project': {
                    '_id': {
                        '$toString': '$_id'
                    },
                    'meter_id': 1,
                    'meter_type': 1,
                    'pods': {
                        '$map': {
                            'input': '$pods',
                            'as': 'pod',
                            'in': {
                                '_id': {
                                    '$toString': '$$pod._id'
                                },
                                'pod_id': '$$pod.pod_id',
                                'pod_type': '$$pod.pod_type'
                            }
                        }
                    }
                }
            }
        ]

        collection = cls.get_motor_collection()
        result = await collection.aggregate(pipeline).to_list(1)
        return result  # Return the first result if exists, else None

    @classmethod
    async def fetch_all_with_pods(cls):
        pipeline = [
            {"$lookup": {
                "from": "podcatalog",
                "localField": "_id",
                "foreignField": "meter_mongo_id.$id",
                "as": "pods"
            }}
        ]
        collection = cls.get_motor_collection()
        return await collection.aggregate(pipeline).to_list(1)


class PODCatalog(Document):
    pod_id: Annotated[int, Indexed(unique=True)]
    pod_type: PODType
    meter_mongo_id: Link[MeterCatalog]

    @classmethod
    async def by_pod_id(cls, pod_id: int) -> Optional["PODCatalog"]:
        """Get an meter by its SQL id."""
        return await cls.find_one(cls.pod_id == pod_id)

    @classmethod
    async def by_many_pod_id(cls, pod_ids: List[int]) -> Optional["PODCatalog"]:
        """Get an meter by its SQL id."""
        pods = await cls.find(In(cls.pod_id, pod_ids)).to_list()
        # Create a dictionary to map pod_ids to pods for quick lookup
        pod_map = {pod.pod_id: pod.id for pod in pods}
        # Reorder the results based on the order of pod_ids provided
        ordered_pods = [pod_map[pod_id]
                        for pod_id in pod_ids if pod_id in pod_map]

        return pod_map, ordered_pods

    @classmethod
    async def by_ids(cls, _ids: List[ObjectId], session=None) -> Optional[List["PODCatalog"]]:
        """Get meters by a list of MongoDB ObjectIds."""
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find({"_id": {"$in": _ids}}, session=session).to_list()

    @classmethod
    async def all(cls):
        """Get meters by a list of MongoDB ObjectIds."""
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find_all().to_list()

    @classmethod
    async def by_meter_id(cls, meter_id: int) -> List["PODCatalog"]:
        """Get pods by meter_id."""
        meter = await MeterCatalog.by_meter_id(meter_id)
        if not meter:
            return []
        query = {"meter_mongo_id.$id": meter.id}
        return await cls.find(query).to_list()


class PODMeasurements(Document):
    pod_id_mongo: Link[PODCatalog]
    timestamp: datetime.datetime
    energy_kwh: float


'''
class ECCatalog(Document):
    ec_id: Annotated[int, Indexed(unique=True)]
    ec_model_id: int
    members_mongo_id: List[Link[PODCatalog]]

    @classmethod
    async def by_ec_id(cls, ec_id: int, db=None) -> Optional["ECCatalog"]:
        if db:
            db.createView( "ECCatalog", "PODCatalog", [
            {
                "$lookup":
                    {
                        "from": "inventory",
                        "localField": "prodId",
                        "foreignField": "prodId",
                        "as": "inventoryDocs"
                    }
            }])
        """Get an meter by its SQL id."""
        return await cls.find_one(cls.ec_id == ec_id)
    
    @classmethod
    async def by_ids(cls, _ids: List[ObjectId], session=None) -> List["ECCatalog"]:
        """Get meters by a list of MongoDB ObjectIds."""
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find({"_id": {"$in": _ids}}, session=session).to_list()
'''


class ECMembersCatalog(Document):
    sharing_key_priority: Optional[int] = None
    sharing_key_percentage: Optional[float] = Field(ge=0, le=100)
    disable_proportional: Optional[bool] = None
    unit_sell_euro_kwh: Optional[float] = None
    pod_mongo_id: Link[PODCatalog]
    pod_type: PODType
    timestamp: datetime.datetime
    ec_id: int

    class Settings:
        collection = "ec_members_catalog"
        indexes = [
            pymongo.IndexModel(
                [("ec_id", 1), ("pod_mongo_id", 1)], unique=True),
            pymongo.IndexModel("ec_id"),
            pymongo.IndexModel("pod_mongo_id")
        ]

    @classmethod
    async def by_ids(cls, _ids: List[ObjectId], session=None) -> Optional[List["ECMembersCatalog"]]:
        """Get meters by a list of MongoDB ObjectIds."""
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find({"_id": {"$in": _ids}}, session=session).to_list()


class AssetsCatalog(Document):
    asset_id: int = Field(
        ..., description="The unique identifier of the asset from the GlobalRegistry DB")
    asset_type: AssetType
    meter_mongo_id: Link[MeterCatalog]

    class Settings:
        collection = "assets_catalog"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("meter_mongo_id", 1)], unique=True),
            pymongo.IndexModel("asset_id", unique=True)
        ]

    @classmethod
    async def by_ids(cls, _ids: List[ObjectId]) -> Optional[List["AssetsCatalog"]]:
        """Get meters by a list of MongoDB ObjectIds."""
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find({"_id": {"$in": _ids}}).to_list()


'''
class AssetCatalog(BaseModel):
    asset_id :int = Field(..., description="The unique identifier of the asset from the GlobalRegistry DB")
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
    
'''
