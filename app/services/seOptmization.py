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
from typing import List


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

        if not await mO.OptimizationRun.exists(run_id):
            raise ValueError(
                f"Optimization run with id {run_id} doesnt exitst")

        docs = []
        for doc in results:
            if not await mC.AssetsCatalog.exists(doc.asset_id):
                raise ValueError(
                    f"Asset id {doc.asset_id} results for optimization run with id {run_id} doesnt exitst")

            docs.append(
                self._initialize_document(
                    mO.AssetOptimizationSchedule,
                    {**doc.model_dump(), "optimization_run_id": run_id}
                )
            )

        await self.create_transaction(
            mO.AssetOptimizationSchedule.insert_many,
            docs
        )

        return
