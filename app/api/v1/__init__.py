from fastapi import APIRouter
from . import (
    catalogs
)

routers = APIRouter()
routers.include_router(catalogs.router)