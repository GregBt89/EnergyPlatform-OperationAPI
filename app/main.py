# FastAPI imports
from .utils.log_setup import logger, add_request_id_middleware
from .db.setup import get_client
from .db import gather_documents
from .core.config import settings as s
from .api import all_routers, __version__
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger  # Import Loguru logger
from beanie import init_beanie
import colorama
colorama.init()

# Application imports

# Description for API documentation
DESCRIPTION = """
This API acts as an intermediate to the operations db
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application services with logging."""
    # Set a default 'request_id' for startup/shutdown logs
    with logger.contextualize(request_id="startup"):
        # Startup event
        logger.info(f"Starting application version {__version__}")
        # Initialize MongoDB client and Beanie ODM
        client = get_client()
        logger.debug(f"Using MongoDB client with id: {id(client)}")
        app.state.mongo_client = client
        await init_beanie(database=getattr(client, s.database_name), document_models=gather_documents())
        logger.info(f"Beanie initialized")
        yield  # Application runs here
        # Shutdown event
        with logger.contextualize(request_id="shutdown"):
            logger.info("Shutting down application")


# Initialize FastAPI app with Loguru integrated lifespan management
app = FastAPI(
    title="Operation DB API",
    description=DESCRIPTION,
    version=__version__,
    lifespan=lifespan
)

# Register all API routers
app.include_router(all_routers)
app.middleware("http")(add_request_id_middleware)
