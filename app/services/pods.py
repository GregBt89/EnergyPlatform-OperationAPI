from fastapi import HTTPException
from ..db.models import (
    pods as p,
    catalogs as c
)
from ..db.enums import PODType
from beanie import Document
from bson import ObjectId
from typing import List, Union, Type, TypeVar, Optional
from ..schemas.measurements import (
    PODMeasurementsIn
)
from .common import CommonServices
from loguru import logger
from datetime import datetime
# Generic type for different measurement schemas
# M = TypeVar("M", PODMeasurementsIn)


class PODsServices(CommonServices):

    async def _inject_measurements(self, measurements: List[PODMeasurementsIn], model_class: Type[p.PODMeasurements]) -> None:
        """
        Generic method to handle the injection of measurements for pods.

        Args:
            measurements (List[M]): List of measurement objects.
            model_class (Type[m.AssetMeasurements]): The Beanie model class to insert documents into.
        """
        # Check for non-existing asset IDs
        not_existing = await self._non_existing_ids(measurements, "pod_id", c.PODCatalog)

        if not_existing:
            logger.error(
                f"Found measurements with non-existing pod ids {not_existing}")
            raise HTTPException(
                status_code=400,
                detail=f"Found measurements with non-existing pod ids {not_existing}"
            )

        # Prepare documents for insertion
        docs = [self._initialize_document(
            model_class, doc.model_dump()) for doc in measurements]

        # Insert documents in a transaction
        await self.create_transaction(model_class.insert_many, docs)

    async def inject_pod_measurements(self, measurements: Union[PODMeasurementsIn, List[PODMeasurementsIn]]) -> None:
        """
        Inject BESS measurements into the database.
        """
        await self._inject_measurements(self._to_list(measurements), p.PODMeasurements)

    async def _get_measurements(self,
                                model: Document,
                                pod_id: Union[int, str, ObjectId],
                                pod_type: PODType,
                                pod_mongo_id: Optional[ObjectId] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                **session_kwargs):

        query = {'pod_type': pod_type}
        if pod_mongo_id:
            try:
                pod_id = ObjectId(pod_mongo_id)
            except Exception:
                raise HTTPException(
                    status_code=400, detail="Invalid pod_id format")
            query['_id'] = pod_id
        else:
            try:
                query["pod_id"] = int(pod_id)
            except Exception:
                raise ValueError("Error converting asset_id to integer")

        # Fetch asset from AssetsCatalog
        pod = await c.PODCatalog.find_one(query)
        logger.debug(f"Found pod {pod}")
        if not pod:
            raise HTTPException(
                status_code=404,
                detail=f"Asset {pod_type.value} with id {pod_id} not found"
            )
        # Ensure the model has the `by_asset_id` method
        if not hasattr(model, 'by_asset_id'):
            raise AttributeError(
                f"Document {model.__name__} does not have a 'by_asset_id' method."
            )

        # Fetch measurements
        measurements = await self.create_transaction(model.by_pod_id, pod.id, start_date, end_date, **session_kwargs)
        measurements[0]["pod_id"] = str(measurements[0]["pod_id"].id)
        return measurements[0]

    async def get_production_pod_measurements(self, pod_id: Union[int, str], pod_mongo_id: Optional[ObjectId] = None, **kwargs):
        # Call create_transaction with the correct model and parameters
        return await self._get_measurements(p.PODMeasurements, pod_id, PODType.PRODUCTION, pod_mongo_id, **kwargs)
