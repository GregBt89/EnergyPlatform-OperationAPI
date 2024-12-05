from typing import Optional
from datetime import datetime
from fastapi import Query
from app.validation.queries import BaseQuery, dataclass

@dataclass
class AssetMeaserementsQuery(BaseQuery):
    asset_id: Optional[int] = Query(
        None, description="An integer corresponding to the asset id (Global Registry db).")
    asset_mongo_id: Optional[str] = Query(
        None, description="A valid mongoDB ObjectId (Operation db).") 
    valid_from: Optional[datetime] = Query(
        None, description="The start date of the forecasts.", serialization_alias="start_date")
    valid_until: Optional[str]= Query(
        None, description="The end date of the forecasts.", serialization_alias="end_date")

    def __post_init__(self):
        # field validation
        self.asset_mongo_id = self._convert_to_object_id("asset_mongo_id")

    
