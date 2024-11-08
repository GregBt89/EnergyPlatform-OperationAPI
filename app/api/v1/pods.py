from fastapi import APIRouter, status, Depends
from ...schemas.measurements import PODMeasurementsIn
from ...services import PODsServices as PS, get_pod_services as gps
from typing import List

router = APIRouter(tags=["PODs"], prefix="/pods")

@router.post("/measurements", status_code=status.HTTP_201_CREATED)
async def add_pod_measurement(measurements: List[PODMeasurementsIn], services: PS = Depends(gps)):
    return await services.inject_pod_measurements(measurements)
