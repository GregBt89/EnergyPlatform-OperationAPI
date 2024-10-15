# FastAPI imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
from loguru import logger  # Import Loguru logger
from beanie import init_beanie
import colorama
colorama.init()

# Application imports
from .api import all_routers, __version__
from .core.config import settings as s
from .db import gather_documents
from .db.setup import get_client
from .utils.log_setup import logger, add_request_id_middleware

# Description for API documentation
DESCRIPTION = """
This API acts as an intermediate to the operations db
"""

# Initialize Loguru to write logs to a file
logger.add("operation_db_api.log", rotation="1 week",
           retention="1 month", level="DEBUG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application services with logging."""
    try:
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

    except Exception as e:
        # Log the error with stack trace
        logger.error(
            f"Error during application initialization: {e}", exc_info=True)
        raise
    finally:
        # Ensure the client is closed on shutdown
        logger.info("Shutting down application.")
        client.close()
        logger.info("MongoDB client closed. Application shutdown complete.")


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
