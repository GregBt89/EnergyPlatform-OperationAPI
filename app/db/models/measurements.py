from beanie import Document, Link
from pydantic import Field
from bson import ObjectId
from loguru import logger
from .catalogs import AssetsCatalog
import pymongo

from typing import Optional
from datetime import datetime


class AssetMeasurements(Document):
    asset_id: Link[AssetsCatalog] = Field(
        ..., description="The unique identifier for the asset")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    exported_power: float = Field(
        ..., description="Power from asset to Grid (kW)")

    class Settings:
        collection = "asset_measurements"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("timestamp", 1)], unique=True),
            pymongo.IndexModel("asset_id")
        ]


class BessMeasurements(Document):

    asset_id:  Link[AssetsCatalog] = Field(
        ..., description="The unique identifier for the asset")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")

    # Lithium battery measurements
    ch_p_u: Optional[float] = Field(
        None, description="Charging power for upward mFRR (kW)")
    dis_p_u: Optional[float] = Field(
        None, description="Discharging power for upward mFRR (kW)")
    ch_p_d: Optional[float] = Field(
        None, description="Charging power for downward mFRR (kW)")
    dis_p_d: Optional[float] = Field(
        None, description="Discharging power for downward mFRR (kW)")
    p_from_vpp: Optional[float] = Field(
        None, description="Power from VPP to battery (kW)")
    p_to_vpp: Optional[float] = Field(
        None, description="Power from battery to VPP (kW)")
    imported_power: float = Field(
        ..., description="Charging power scheduled for the day-ahead market (kW).")
    exported_power: float = Field(
        ..., description="Discharging power scheduled for the day-ahead market (kW).")
    # Degradation data for lithium battery
    degradation_cal: Optional[float] = Field(
        None, description="Calendar degradation of battery (kWh)")
    degradation_cyc: Optional[float] = Field(
        None, description="Cycle degradation of battery (kWh)")
    soc: float = Field(...,
                       description="State of charge of the battery (kWh)")

    class Settings:
        collection = "bess_measurements"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("timestamp", 1)], unique=True),
            pymongo.IndexModel("asset_id")
        ]

    @classmethod
    async def by_asset_id(cls, asset_id: str, start_date=None, end_date=None, session=None):
        query = {
            'asset_id': {
                '$ref': 'AssetsCatalog',
                '$id': ObjectId(asset_id)
            }
        }
        # Add date range filtering if both start_date and end_date are provided
        if start_date and end_date:
            query['timestamp'] = {
                '$gte': start_date,
                '$lte': end_date
            }
        elif start_date:
            # If only start_date is provided, match all records after this date
            query['timestamp'] = {'$gte': start_date}
        elif end_date:
            # If only end_date is provided, match all records before this date
            query['timestamp'] = {'$lte': end_date}

        s1 = {
            '$match': query
        }
        s2 = {
            '$group': {
                '_id': '$asset_id',
                'timestamps': {
                    '$push': '$timestamp'
                },
                'ch_p_u': {
                    '$push': '$ch_p_u'
                },
                'dis_p_u': {
                    '$push': '$dis_p_u'
                },
                'ch_p_d': {
                    '$push': '$ch_p_d'
                },
                'dis_p_d': {
                    '$push': '$dis_p_d'
                },
                'p_from_vpp': {
                    '$push': '$p_from_vpp'
                },
                'p_to_vpp': {
                    '$push': '$p_to_vpp'
                },
                'imported_power': {
                    '$push': '$imported_power'
                },
                'exported_power': {
                    '$push': '$exported_power'
                },
                'degradation_cal': {
                    '$push': '$degradation_cal'
                },
                'degradation_cyc': {
                    '$push': '$degradation_cyc'
                },
                'soc': {
                    '$push': '$soc'
                }
            }}

        s3 = {
            '$addFields': {
                # Convert the document fields into an array of key-value pairs
                'fields': {
                    '$objectToArray': '$$ROOT'
                }
            }
        }

        s4 = {
            '$addFields': {
                # Process each field and check if it's an array of nulls
                'fields': {
                    '$map': {
                        'input': '$fields',
                        'as': 'field',
                        'in': {
                            'k': '$$field.k',  # Keep the original field name
                            'v': {
                                '$cond': {
                                    'if': {
                                        '$and': [
                                            # Check if the field is an array
                                            {'$isArray': '$$field.v'},
                                            {'$allElementsTrue': [{'$map': {'input': '$$field.v', 'as': 'item', 'in': {
                                                '$eq': ['$$item', None]}}}]}  # Check if all elements are null
                                        ]
                                    },
                                    'then': None,  # Set to null if all elements are null
                                    'else': '$$field.v'  # Keep the original value otherwise
                                }
                            }
                        }
                    }
                }
            }
        }

        s5 = {
            # Convert the array of key-value pairs back into an object
            '$replaceRoot': {
                'newRoot': {'$arrayToObject': '$fields'}
            }
        }

        s6 = {
            '$project': {
                '_id': 0,
                'asset_id': '$_id',
                'timestamps': 1,
                'ch_p_u': 1,
                'dis_p_u': 1,
                'ch_p_d': 1,
                'dis_p_d': 1,
                'p_from_vpp': 1,
                'p_to_vpp': 1,
                'imported_power': 1,
                'exported_power': 1,
                'degradation_cal': 1,
                'degradation_cyc': 1,
                'soc': 1
            }
        }
        pipeline = [s1, s2, s3, s4, s5, s6]
        # Execute the async query and return the result as a list
        collection = cls.get_motor_collection()
        return await collection.aggregate(pipeline, session=session).to_list(1)


class PvppMeasurements(Document):
    asset_id: Link[AssetsCatalog] = Field(
        ..., description="The unique identifier for the asset")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    exported_power: float = Field(
        ..., description="Power from asset to Grid (kW)")

    class Settings:
        collection = "pvpp_measurements"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("timestamp", 1)], unique=True),
            pymongo.IndexModel("asset_id")
        ]

    @classmethod
    async def by_asset_id(cls, asset_id: str, start_date=None, end_date=None, session=None):
        logger.debug(f"Preparing query to {cls} by asset mongo id")
        query = {
            'asset_id': {
                '$ref': 'AssetsCatalog',
                '$id': ObjectId(asset_id)
            }
        }
        # Add date range filtering if both start_date and end_date are provided
        if start_date and end_date:
            query['timestamp'] = {
                '$gte': start_date,
                '$lte': end_date
            }
        elif start_date:
            # If only start_date is provided, match all records after this date
            query['timestamp'] = {'$gte': start_date}
        elif end_date:
            # If only end_date is provided, match all records before this date
            query['timestamp'] = {'$lte': end_date}

        s1 = {
            '$match': query
        }
        s2 = {
            '$group': {
                '_id': '$asset_id',
                'timestamps': {
                    '$push': '$timestamp'
                },
                'exported_power': {
                    '$push': '$exported_power'
                }
            }}
        s3 = {
            '$project': {
                '_id': 0,
                'asset_id': '$_id',
                'timestamps': 1,
                'exported_power': 1
            }
        }

        pipeline = [s1, s2, s3]
        # Execute the async query and return the result as a list
        collection = cls.get_motor_collection()
        return await collection.aggregate(pipeline, session=session).to_list(1)


class WppMeasurements(Document):
    asset_id: Link[AssetsCatalog] = Field(
        ..., description="The unique identifier for the asset")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    exported_power: float = Field(
        ..., description="Power from asset to Grid (kW)")

    class Settings:
        collection = "wpp_measurements"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("timestamp", 1)], unique=True),
            pymongo.IndexModel("asset_id")
        ]

    @classmethod
    async def by_asset_id(cls, asset_id: str, start_date=None, end_date=None, session=None):
        logger.debug(f"Preparing query to {cls} by asset mongo id")
        query = {
            'asset_id': {
                '$ref': 'AssetsCatalog',
                '$id': ObjectId(asset_id)
            }
        }
        # Add date range filtering if both start_date and end_date are provided
        if start_date and end_date:
            query['timestamp'] = {
                '$gte': start_date,
                '$lte': end_date
            }
        elif start_date:
            # If only start_date is provided, match all records after this date
            query['timestamp'] = {'$gte': start_date}
        elif end_date:
            # If only end_date is provided, match all records before this date
            query['timestamp'] = {'$lte': end_date}

        s1 = {
            '$match': query
        }
        s2 = {
            '$group': {
                '_id': '$asset_id',
                'timestamps': {
                    '$push': '$timestamp'
                },
                'exported_power': {
                    '$push': '$exported_power'
                }
            }}
        s3 = {
            '$project': {
                '_id': 0,
                'asset_id': '$_id',
                'timestamps': 1,
                'exported_power': 1
            }
        }
        pipeline = [s1, s2, s3]
        # Execute the async query and return the result as a list
        collection = cls.get_motor_collection()
        return await collection.aggregate(pipeline, session=session).to_list(10)


class HydroMeasurements(Document):
    asset_id: Link[AssetsCatalog] = Field(
        ..., description="The unique identifier for the asset")
    timestamp: datetime = Field(
        ..., description="Time of the measurement")
    exported_power: float = Field(
        ..., description="Power from asset to Grid (kW)")

    class Settings:
        collection = "wpp_measurements"
        indexes = [
            pymongo.IndexModel(
                [("asset_id", 1), ("timestamp", 1)], unique=True),
            pymongo.IndexModel("asset_id")
        ]

    @ classmethod
    async def by_asset_id(cls, asset_id: str, start_date=None, end_date=None, session=None):
        logger.debug(f"Preparing query to {cls} by asset mongo id")
        query = {
            'asset_id': {
                '$ref': 'AssetsCatalog',
                '$id': ObjectId(asset_id)
            }
        }
        # Add date range filtering if both start_date and end_date are provided
        if start_date and end_date:
            query['timestamp'] = {
                '$gte': start_date,
                '$lte': end_date
            }
        elif start_date:
            # If only start_date is provided, match all records after this date
            query['timestamp'] = {'$gte': start_date}
        elif end_date:
            # If only end_date is provided, match all records before this date
            query['timestamp'] = {'$lte': end_date}

        s1 = {
            '$match': query
        }
        s2 = {
            '$group': {
                '_id': '$asset_id',
                'timestamps': {
                    '$push': '$timestamp'
                },
                'exported_power': {
                    '$push': '$exported_power'
                }
            }}
        s3 = {
            '$project': {
                '_id': 0,
                'asset_id': '$_id',
                'timestamps': 1,
                'exported_power': 1
            }
        }
        pipeline = [s1, s2, s3]
        # Execute the async query and return the result as a list
        collection = cls.get_motor_collection()
        return await collection.aggregate(pipeline, session=session).to_list(1)
