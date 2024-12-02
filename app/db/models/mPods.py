from beanie import Document, Link
from pydantic import Field
from bson import ObjectId
from loguru import logger
from .mCatalogs import PODCatalog
import pymongo
from datetime import timezone
from typing import Optional
from datetime import datetime


class PODMeasurements(Document):
    pod_id: Link[PODCatalog] = Field(
        ..., description="The unique identifier for the POD")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    surplus: float = Field(
        ..., description="Surplus energy to grid (kWh)")
    consumption: float = Field(
        ..., description="Energy consummed from Grid (kWh)")

    class Settings:
        collection = "pod_measurements"
        indexes = [
            pymongo.IndexModel(
                [("pod_id", 1), ("timestamp", 1)], unique=True),
            pymongo.IndexModel("pod_id")
        ]


view = [
    {
        '$match': {
            'timestamp': {
                '$gte': datetime(2023, 7, 1, 0, 0, 0, tzinfo=timezone.utc),
                '$lt': datetime(2023, 7, 7, 0, 0, 0, tzinfo=timezone.utc)
            }
        }
    }, {
        '$lookup': {
            'from': 'PODCatalog',
            'localField': 'pod_id.$id',
            'foreignField': '_id',
            'as': 'podDetails'
        }
    }, {
        '$unwind': {
            'path': '$podDetails'
        }
    }, {
        '$lookup': {
            'from': 'MeterCatalog',
            'localField': 'podDetails.meter_mongo_id.$id',
            'foreignField': '_id',
            'as': 'meterDetails'
        }
    }, {
        '$unwind': {
            'path': '$meterDetails'
        }
    }, {
        '$project': {
            '_id': 0,
            'timestamp': {
                '$dateToString': {
                    'format': '%Y-%m-%d_%H-%M-%S',
                    'date': '$timestamp'
                }
            },
            'net': {
                '$sum': [
                    '$consumption', '$surplus'
                ]
            },
            'meterDetails': 1
        }
    }, {
        '$group': {
            '_id': '$meterDetails',
            'netDictionary': {
                '$push': {
                    'k': {
                        '$toString': '$timestamp'
                    },
                    'v': '$net'
                }
            }
        }
    }, {
        '$project': {
            '_id': 0,
            'meterDetails': '$_id',
            'net': {
                '$arrayToObject': '$netDictionary'
            }
        }
    }
]
