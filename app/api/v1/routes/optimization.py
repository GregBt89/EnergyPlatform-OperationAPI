from fastapi import APIRouter, status, Depends, Query
from typing import List, Optional, Annotated
from loguru import logger
from datetime import datetime
from app.services import (
    OptimizationServices as PS,
    get_optimization_services as gos
)
from app.validation.schemas.shOptimization import (
    OptimizationRun,
    OptimizationRunResponse,
    AssetOptimizationResults,
    AssetOptimizationResultsResponse,
    OptimizationRuResultsResponse
)
from app.validation.queries.vqOptimization import(
    AssetOptimizationQuery
)
from app.utils.types import PydanticObjectId

router = APIRouter(prefix='/optimization', tags=["Optimization"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=OptimizationRunResponse, response_model_exclude_none=True)
async def store_optimization_run(
        run_details: OptimizationRun,
        services: PS = Depends(gos)
):
    logger.info('Creating a new optimization run')
    return await services.create_new_optimization_run(run_details)


@router.post("/{run_id:str}", status_code=status.HTTP_201_CREATED)
async def store_asset_optimization_results(
        run_id: PydanticObjectId,
        results: List[AssetOptimizationResults],
        services: PS = Depends(gos)
):
    logger.info(f"Storing asset results for optimization run with ID {run_id}")
    return await services.store_asset_optimization_results(run_id, results)


@router.get("", response_model=List[OptimizationRuResultsResponse], response_model_exclude_none=True)
async def get_optimization_run(query: AssetOptimizationQuery = Depends(), 
    services: PS = Depends(gos)
):
    return await services.get_optimization_run_results(query)


@router.get("/assets/{asset_id:str}", response_model=Optional[List[AssetOptimizationResultsResponse]], response_model_exclude_none=True)
async def get_asset_optimization_results(
    asset_id: str,
    run_id: Optional[PydanticObjectId] = None,
    services: PS = Depends(gos)
):
    return await services.get_asset_optimization_results(asset_id, run_id)

