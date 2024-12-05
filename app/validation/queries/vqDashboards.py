from dataclasses import dataclass
from typing import Optional, Union
from datetime import datetime
from bson import ObjectId
from fastapi import Query

@dataclass
class AssetDashboardQuery:
    asset_id: Union[int, str] = Query(...,
                                      description="An integer or a valid MongoDB ObjectId")
    valid_from: Optional[datetime] = Query(
        None, description="The datetime that the forecasts is valid_from.")
    forecast_id: Optional[str] = Query(
        None, description="The mongo db _id for the specific forecast", serialization_alias="_id")
    

if __name__ == "__main__":
    query = AssetDashboardQuery(16, datetime.now())
    print(query)