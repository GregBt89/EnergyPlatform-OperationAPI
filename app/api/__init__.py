__version__ = "1.0.0"

from fastapi import APIRouter
from .v1 import routers as v1_routers

all_routers = APIRouter()
all_routers.include_router(v1_routers)
