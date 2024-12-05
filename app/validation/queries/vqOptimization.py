from typing import Optional
from datetime import datetime
from fastapi import Query
from app.validation.queries import BaseQuery, dataclass

@dataclass
class AssetOptimizationQuery(BaseQuery):
    run_id: Optional[str] = Query(
        None, description="The mongo db _id for the optimization run.", serialization_alias="_id")
    valid_from:Optional[datetime] = Query(
        None, description="The start date of the optimization run.")
    schedules: Optional[bool] = Query(
        False, description="Whether to include or not the optimization results.")
    
    def __post_init__(self):
        # Validate and convert to ObjectId
        self.run_id = self._convert_to_object_id("run_id")