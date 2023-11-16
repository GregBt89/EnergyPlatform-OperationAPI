# Fast api imports
from fastapi import FastAPI
from contextlib import asynccontextmanager
import colorama; colorama.init()
# Mongodb imports
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

# app imports
from .db import gather_documents
from .utils.config import settings as s
from .routers import assets

uri = "mongodb://{}:{}/{}".format(s.database_hostname, s.database_port, s.database_name)
uri = "mongodb://localhost:27017"

DESCRIPTION = """
This API acts as an intermeediate to the operations db

"""

@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore
    """Initialize application services."""
    client = AsyncIOMotorClient(uri).operation  # type: ignore[attr-defined]
    await init_beanie(client, document_models=gather_documents())  # type: ignore[arg-type,attr-defined]
    print("Startup complete")
    yield
    print("Shutdown complete")


app = FastAPI(
    title="Operation DB API",
    description=DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(assets.router)