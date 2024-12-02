from app.db.models import (
    mOptimization as mO,
    mCatalogs as mC
)
from app.services.seCommon import CommonServices
from app.schemas.shOptimization import (
    OptimizationRun,
    OptimizationRunResponse,
    AssetOptimizationResults
)
from loguru import logger
from app.utils.types import PydanticObjectId
from typing import List, Optional
from bson import ObjectId


class OptimizationServices(CommonServices):

    async def create_new_optimization_run(
            self,
            run: OptimizationRun
    ) -> OptimizationRunResponse:

        doc = self._initialize_document(
            mO.OptimizationRun,
            run.model_dump()
        )

        doc = await self.create_transaction(mO.OptimizationRun.insert_one, doc)
        return {**run.model_dump(), "run_id": doc.id}

    async def store_asset_optimization_results(
            self,
            run_id: PydanticObjectId,
            results=List[AssetOptimizationResults]
    ) -> None:
        run = await mO.OptimizationRun.exists(run_id)
        if not run:
            raise ValueError(
                f"Optimization run with id {run_id} doesnt exitst")

        docs = []
        for doc in results:
            if not await mC.AssetsCatalog.exists(doc.asset_id):
                raise ValueError(
                    f"Asset id {doc.asset_id} results for optimization run with id {run_id} doesnt exitst")
            print(doc.model_dump())
            docs.append(
                self._initialize_document(
                    mO.AssetOptimizationSchedule,
                    {**doc.model_dump(), "optimization_run_id": run.id}
                )
            )

        await self.create_transaction(
            mO.AssetOptimizationSchedule.insert_many,
            docs
        )

        return

    async def get_optimization_run(self, run_id: str, schedules: Optional[bool] = False):

        run_id = self._to_ObjectId(run_id)

        run = await mO.OptimizationRun.exists(run_id, links=False)
        if not run:
            raise ValueError(
                f"Optimization run with id {run_id} doesnt exitst")

        if schedules:
            logger.debug("Some mongodb servers (AWS DocDB) do not support correlated subqueries." +
                         "Using second direct query for optimization results")
            run.asset_schedules = await mO.AssetOptimizationSchedule.by_optimization_run_id(run_id)
        return run

    async def get_asset_optimization_results(self, asset_id: PydanticObjectId, run_id: Optional[PydanticObjectId]):

        # run_id = self._to_ObjectId(run_id)

        asset_results = await mO.AssetOptimizationSchedule.exists(asset_id, run_id)
        if not asset_results:
            msg = f"No results found for asset - {asset_id}"
            if run_id:
                msg += f" and optimization_run - {run_id}"
            logger.info(msg)
        return asset_results
