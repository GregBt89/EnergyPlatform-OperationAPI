from motor.motor_asyncio import AsyncIOMotorClient
from functools import lru_cache

URI = "mongodb://localhost:27017/?replicaSet=rs0"

@lru_cache()
def get_client():
    """Create and cache MongoDB client."""
    return AsyncIOMotorClient(URI)
