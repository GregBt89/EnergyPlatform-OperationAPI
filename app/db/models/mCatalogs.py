from beanie import Document, Link, Indexed
from pydantic import BaseModel, Field
from bson import ObjectId
from beanie.operators import In
import pymongo

from app.utils.types import PydanticObjectId
from typing import Optional, List, Annotated
import datetime
from ..enums import PODType, MeterType, ECType, AssetType


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
    meter_mongo_id: PydanticObjectId = Field(
        ..., description="the id of the meter from MeterCatalog not the sql.")

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


class ECMembersCatalog(Document):
    sharing_key_priority: Optional[int] = None
    sharing_key_percentage: Optional[float] = Field(ge=0, le=100)
    disable_proportional: Optional[bool] = None
    unit_sell_euro_kwh: Optional[float] = None
    pod_mongo_id: PydanticObjectId = Field(
        ..., description="The id of the POD from PODCatalog, not the sql.")
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
    meter_mongo_id: PydanticObjectId = Field(
        ..., description="The id of the meter from MeterCatalog, not the sql")

    class Settings:
        collection = "assets_catalog"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("meter_mongo_id", 1)], unique=True),
            pymongo.IndexModel("asset_id", unique=True)
        ]

    @classmethod
    async def by_ids(cls, _ids: List[ObjectId]) -> Optional[List["AssetsCatalog"]]:
        # Use the $in operator to query for documents with _id in _ids list
        return await cls.find({"_id": {"$in": _ids}}).to_list()

    @classmethod
    async def by_asset_id(cls, asset_id: int) -> Optional["AssetsCatalog"]:
        return await cls.find_one({"asset_id": asset_id})

    @classmethod
    async def all(cls) -> Optional["AssetsCatalog"]:
        return await cls.find_all().to_list()

    @classmethod
    async def exists(clc, _id: PydanticObjectId) -> bool:
        if await clc.find_one({"_id": ObjectId(_id)}):
            return True
        return False
