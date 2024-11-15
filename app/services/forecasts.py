from fastapi import HTTPException
from ..db.models import (
    forecasts as f
)
from ..db.enums import AssetType
from beanie import Document
from bson import ObjectId
from typing import List, Union, Type, TypeVar, Optional
from ..schemas.forecasts import (
    Forecasts
)
from .common import CommonServices
from loguru import logger
from datetime import datetime


class ForecastServices(CommonServices):

    async def inject_asset_forecasts(
            self,
            asset_id: str,
            forecasts: Union[Forecasts, List[Forecasts]]
    ) -> None:
        # Convert to list 
        forecasts = self._to_list(forecasts)
        # Initialize documents
        docs = [self._initialize_document(
            f.AssetForecast, doc.model_dump()) for doc in forecasts]
        # Insert documents within a transaction
        await self.create_transaction(f.AssetForecast.insert_many, docs)

    async def inject_pod_forecasts(self, pod_id: str, forecasts: List[Forecasts]):
        docs = [self._initialize_document(
            f.PodForecast, doc.model_dump()) for doc in forecasts]
        # Insert documents in a transaction
        await self.create_transaction(f.PodForecast.insert_many, docs)

    async def inject_market_forecasts(self, pod_id: str, forecasts: List[Forecasts]):
        docs = [self._initialize_document(
            f.MarketForecast, doc.model_dump()) for doc in forecasts]
        # Insert documents in a transaction
        await self.create_transaction(f.MarketForecast.insert_many, docs)

    async def get_asset_forecasts(self):
        #!TODO Add conditional search
        return await f.AssetForecast.all()
