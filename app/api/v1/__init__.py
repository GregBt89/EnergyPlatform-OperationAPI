from fastapi import APIRouter
from app.api.v1.routes import (
    catalogs,
    assets,
    pods,
    forecasts,
    optimization
)

routers = APIRouter()
routers.include_router(catalogs.router)
routers.include_router(assets.router)
routers.include_router(pods.router)
routers.include_router(forecasts.router)
routers.include_router(optimization.router)
