
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from motor.core import AgnosticClient
from typing import Type, TypeVar
from ..db.setup import get_client
from .common import CommonServices
from .catalogs import CatalogServices
from .measurements import MeasurementServices

# Define a TypeVar for the service class
T = TypeVar("T", bound=CommonServices)


async def _get_service(
    service_class: Type[T],
    client: AgnosticClient = Depends(get_client)
) -> T:
    """
    Generalized service getter that returns the service_class instance.
    """
    return service_class(client)


# Use the get_service function to dynamically instantiate services
async def get_common_services(client: AgnosticClient = Depends(get_client)) -> CommonServices:
    return await _get_service(CommonServices, client)


async def get_catalog_services(client: AgnosticClient = Depends(get_client)) -> CatalogServices:
    return await _get_service(CatalogServices, client)


async def get_measurement_services(client: AgnosticClient = Depends(get_client)) -> MeasurementServices:
    return await _get_service(MeasurementServices, client)
