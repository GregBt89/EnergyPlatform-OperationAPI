# Fast api imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
import colorama; colorama.init()
# Mongodb imports
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from .db.config import get_client

# app imports
from .db import gather_documents
from .utils.config import settings as s
from .routers import catalogs, pods, ecomunities

uri = "mongodb://{}:{}/{}".format(s.database_hostname, s.database_port, s.database_name)
URI = "mongodb://localhost:27017"

DESCRIPTION = """
This API acts as an intermediate to the operations db
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application services."""
    try:
        client = get_client()
        # Initialize Beanie with the database 'operation' and document models
        await init_beanie(database=client.operation, document_models=gather_documents())
        print("Startup complete")
        yield
    except Exception as e:
        print(f"Error during application initialization: {str(e)}")
        raise
    finally:
        print("Shutdown complete")
        client.close()

app = FastAPI(
    title="Operation DB API",
    description=DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(catalogs.router)
app.include_router(pods.router)
#app.include_router(ecomunities.router)