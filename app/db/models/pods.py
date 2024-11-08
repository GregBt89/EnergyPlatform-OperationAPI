from beanie import Document, Link
from pydantic import Field
from bson import ObjectId
from loguru import logger
from .catalogs import PODCatalog
import pymongo

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
