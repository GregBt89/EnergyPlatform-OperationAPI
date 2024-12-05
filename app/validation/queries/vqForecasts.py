
from fastapi import Query
from typing import Optional, Union
from datetime import datetime
from bson import ObjectId
from app.validation.queries import BaseQuery, dataclass

@dataclass
class AssetForecastsQuery(BaseQuery):
    asset_id: Union[int, str] = Query(
        ..., description="An integer or a valid MongoDB ObjectId")
    valid_from: Optional[datetime] = Query(
        None, description="The datetime that the forecasts is valid_from.")
    forecast_id: Optional[str] = Query(
        None, description="The mongo db _id for the specific forecast", serialization_alias="_id")
        
    def _validate_asset_id(self):
        value = self.asset_id
        # Convert to integer if it's numeric
        if value.isdigit(): 
            return int(value)
        if ObjectId.is_valid(value):
            # Convert to ObjectId if it is a valid ObjectId string
            return ObjectId(value)
        raise ValueError(
            "asset_id must be either an integer or a valid ObjectId string")
    
    def _validate_forecast_id(self):
        value = self.forecast_id
        if value:
            if ObjectId.is_valid(value):
                # Convert to ObjectId if it is a valid ObjectId string
                return ObjectId(value)
            raise ValueError(
                "forecast_id must be a valid ObjectId string")
        
    def __post_init__(self):
        # Validate `asset_id`
        self.asset_id = self._validate_asset_id()
        # Validate `forecast_id`
        self.forecast_id = self._validate_forecast_id()
