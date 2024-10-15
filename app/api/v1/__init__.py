from fastapi import APIRouter
from . import (
    catalogs,
    assets
)

routers = APIRouter()
routers.include_router(catalogs.router)
routers.include_router(assets.router)
