
from fastapi import Depends
from motor.core import AgnosticClient
from typing import Type, TypeVar
from ..db.setup import get_client
from .seCommon import CommonServices
from .seCatalogs import CatalogServices
from .seMeasurements import MeasurementServices
from .sePods import PODsServices
from .seForecasts import ForecastServices
from .seOptmization import OptimizationServices

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


async def get_pod_services(client: AgnosticClient = Depends(get_client)) -> PODsServices:
    return await _get_service(PODsServices, client)


async def get_forecast_services(client: AgnosticClient = Depends(get_client)) -> ForecastServices:
    return await _get_service(ForecastServices, client)


async def get_optimization_services(client: AgnosticClient = Depends(get_client)) -> OptimizationServices:
    return await _get_service(OptimizationServices, client)
