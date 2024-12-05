from fastapi import HTTPException
from ..db.models import (
    mCatalogs as c,
    mForecasts as f
)
from ..db.enums import AssetType
from beanie import Document
from bson import ObjectId
from typing import List, Union, Type, TypeVar, Optional
from app.validation.schemas.shForecasts import (
    Forecasts
)
from app.validation.queries.vqForecasts import (
    AssetForecastsQuery
)
from .seCommon import CommonServices
from loguru import logger
from datetime import datetime


class ForecastServices(CommonServices):

    async def inject_asset_forecasts(
            self,
            asset_id: str,
            forecasts: Union[Forecasts, List[Forecasts]]
    ) -> None:
        # Validate the asset_id exists in the AssetsCatalog
        exists = await c.AssetsCatalog.find_one({"_id": ObjectId(asset_id)})
        if not exists:
            raise ValueError(
                f"Referenced asset_id {asset_id} does not exist in AssetsCatalog.")

        # Convert to list
        forecasts = self._to_list(forecasts)
        # Initialize documents
        docs = [
            self._initialize_document(
                f.AssetForecast, {**doc.model_dump(), "asset_id": asset_id}
            )
            for doc in forecasts
        ]
        # Insert documents within a transaction
        await self.create_transaction(f.AssetForecast.insert_many, docs)

    async def inject_pod_forecasts(self, pod_id: str, forecasts: List[Forecasts]):
        docs = [self._initialize_document(
            f.PodForecast, {**doc.model_dump(), "pod_id": pod_id}) for doc in forecasts]
        # Insert documents in a transaction
        await self.create_transaction(f.PodForecast.insert_many, docs)

    async def inject_market_forecasts(self, pod_id: str, forecasts: List[Forecasts]):
        docs = [self._initialize_document(
            f.MarketForecast, doc.model_dump()) for doc in forecasts]
        # Insert documents in a transaction
        await self.create_transaction(f.MarketForecast.insert_many, docs)

    async def get_asset_forecasts(self, query: AssetForecastsQuery) -> Union[None, List[f.AssetForecast]]:
        if query.forecast_id:
            return await f.AssetForecast.find_one(
                {"_id": ObjectId(query.forecast_id)}
                )
        if query.asset_id:
            if isinstance(query.asset_id, int):
                asset = await c.AssetsCatalog.find_one({"asset_id":query["asset_id"]})
                query.asset_id = asset.id if asset else query.asset_id
                # Search by sql_id
                return await f.AssetForecast.find_by_sql_id(
                    query.model_dump(exclude_none=True)
                    )
            elif ObjectId.is_valid(query.asset_id):
                query.asset_id = ObjectId(query.asset_id)
                # Search by mongo_id
                return await f.AssetForecast.find_by_mongo_id(
                    query.model_dump(exclude_none=True)
                    )
        else:
            # Return all forecasts
            return await f.AssetForecast.all()

    async def get_pod_forecasts(self, pod_id):
        #!TODO Add conditional search
        if pod_id:
            if isinstance(pod_id, int):
                # Search by sql_id
                forecasts = await f.PodForecast()
            elif ObjectId.is_valid():
                # Search by mongo_id
                forecasts = await f.PodForecast()
        else:
            # Return all forecasts
            forecasts = await f.AssetForecast.all()

        return forecasts
