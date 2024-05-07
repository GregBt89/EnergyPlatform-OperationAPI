from fastapi import APIRouter, status, HTTPException
from ..internal import schemas
from ..db import models 
from typing import List

router = APIRouter(tags=["PODs"], prefix="/pods")

@router.post("/measurements", status_code=status.HTTP_201_CREATED)
async def add_pod_meqsurement(new_measurements: List[schemas.PODMeasurements]):

    measurements = list(); pods = dict()

    for new_measurement in new_measurements:
        if new_measurement.pod_id not in pods.keys():
            pod = await models.PODCatalog.by_pod_id(new_measurement.pod_id)
            if not pod:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'POD {new_measurement.pod_id} not found.')
            pods[new_measurement.pod_id] = pod.id
    
        measurements.append(
            models.PODMeasurements(
                pod_id_mongo=pods[new_measurement.pod_id],
                timestamp=new_measurement.timestamp,
                energy_kwh=new_measurement.energy_kwh
                ))
    
    await models.PODMeasurements.insert_many(measurements)

    return 

