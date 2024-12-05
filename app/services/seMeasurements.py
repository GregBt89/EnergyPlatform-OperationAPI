from fastapi import HTTPException
from ..db.models import (
    mCatalogs as c,
    mMeasurements as m
)
from ..db.enums import AssetType
from beanie import Document
from bson import ObjectId
from typing import List, Union, Type, TypeVar, Optional
from app.validation.schemas.shMeasurements import (
    BessMeasurementsIn,
    AssetMeasurementsIn
)
from app.validation.queries.vqMeasurements import(
    AssetMeaserementsQuery
)
from .seCommon import CommonServices
from loguru import logger
from datetime import datetime
# Generic type for different measurement schemas
M = TypeVar("M", BessMeasurementsIn, AssetMeasurementsIn)

class MeasurementServices(CommonServices):

    async def _inject_measurements(self, measurements: List[M], model_class: Type[m.AssetMeasurements]) -> None:
        """
        Generic method to handle the injection of measurements for different asset types.

        Args:
            measurements (List[M]): List of measurement objects.
            model_class (Type[m.AssetMeasurements]): The Beanie model class to insert documents into.
        """
        # Check for non-existing asset IDs
        not_existing = await self._non_existing_ids(measurements, "asset_id", c.AssetsCatalog)

        if not_existing:
            logger.error(
                f"Found measurements with non-existing asset ids {not_existing}")
            raise HTTPException(
                status_code=400,
                detail=f"Found measurements with non-existing asset ids {not_existing}"
            )

        # Prepare documents for insertion
        docs = [self._initialize_document(
            model_class, doc.model_dump()) for doc in measurements]

        # Insert documents in a transaction
        await self.create_transaction(model_class.insert_many, docs)

    async def inject_bess_measurements(self, measurements: Union[BessMeasurementsIn, List[BessMeasurementsIn]]) -> None:
        """
        Inject BESS measurements into the database.
        """
        await self._inject_measurements(self._to_list(measurements), m.BessMeasurements)

    async def inject_pvpp_measurements(self, measurements: Union[AssetMeasurementsIn, List[AssetMeasurementsIn]]) -> None:
        """
        Inject PVPP measurements into the database.
        """
        await self._inject_measurements(self._to_list(measurements), m.PvppMeasurements)

    async def inject_wpp_measurements(self, measurements: Union[AssetMeasurementsIn, List[AssetMeasurementsIn]]) -> None:
        """
        Inject WPP measurements into the database.
        """
        await self._inject_measurements(self._to_list(measurements), m.WppMeasurements)

    async def inject_hydro_measurements(self, measurements: Union[AssetMeasurementsIn, List[AssetMeasurementsIn]]) -> None:
        """
        Inject Hydro measurements into the database.
        """
        await self._inject_measurements(self._to_list(measurements), m.HydroMeasurements)

    async def _get_measurements(self,
                                model: Document,
                                asset_type: AssetType,
                                query:AssetMeaserementsQuery,
                                **session_kwargs):
        
        query_dict = {'asset_type': asset_type}
        if query.asset_mongo_id:
            query_dict['_id'] = query.asset_mongo_id
        else:
            query_dict["asset_id"] = query.asset_id


        # Fetch asset from AssetsCatalog
        asset = await m.AssetsCatalog.find_one(query)
        logger.debug(f"Found asset {asset}")
        if not asset:
            raise ValueError(
                f"Asset {asset_type.value} with id {query.asset_id if query.asset_id else query.asset_mongo_id} not found"
            )
        # Ensure the model has the `by_asset_id` method
        if not hasattr(model, 'by_asset_id'):
            raise AttributeError(
                f"Document {model.__name__} does not have a 'by_asset_id' method."
            )

        # Fetch measurements
        measurements = await self.create_transaction(model.by_asset_id, asset.id, query.start_date, query.end_date, **session_kwargs)
        measurements[0]["asset_id"] = str(measurements[0]["asset_id"].id)
        return measurements[0]

    async def get_bess_measurements(self, query_params: AssetMeaserementsQuery):
        # Call create_transaction with the correct model and parameters
        return await self._get_measurements(m.BessMeasurements, AssetType.BESS, query_params)

    async def get_pvpp_measurements(self, asset_id: Union[int, str], asset_mongo_id: Optional[ObjectId] = None, **kwargs):
        # Call create_transaction with the correct model and parameters
        return await self._get_measurements(m.PvppMeasurements, asset_id, AssetType.PVPP, asset_mongo_id, **kwargs)

    async def get_wpp_measurements(self, asset_id: Union[int, str], asset_mongo_id: Optional[ObjectId] = None, **kwargs):
        # Call create_transaction with the correct model and parameters
        return await self._get_measurements(m.WppMeasurements, asset_id, AssetType.WPP, asset_mongo_id, **kwargs)

    async def get_hpp_measurements(self, asset_id: Union[int, str], asset_mongo_id: Optional[ObjectId] = None, **kwargs):
        # Call create_transaction with the correct model and parameters
        return await self._get_measurements(m.HydroMeasurements, asset_id, AssetType.HYDRO, asset_mongo_id, **kwargs)
