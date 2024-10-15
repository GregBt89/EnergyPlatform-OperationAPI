from fastapi import Request
import uuid
import contextvars
from loguru import logger
import sys
import time

# Create a context variable to store the request ID (UUID)
request_id_context = contextvars.ContextVar("request_id", default=None)

# Define a log format that includes the request ID (UUID)
log_format = "<green>{time}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | {message} | <yellow>{extra[request_id]}</yellow>"

# Configure Loguru to use the format
logger.configure(handlers=[{"sink": sys.stdout, "format": log_format}])

# Add file logging with rotation and retention, also including the UUID
logger.add("opApi.log", format=log_format, rotation="1 week",
           retention="1 month", level="DEBUG")

# Middleware to add a unique request ID (UUID) to each incoming request
async def add_request_id_middleware(request: Request, call_next):
    # Generate a UUID for the request
    request_id = str(uuid.uuid4())

    # Set the request_id in the context variable
    request_id_context.set(request_id)

    # Add the request_id to the Loguru "extra" context
    with logger.contextualize(request_id=request_id):
        logger.info(f"New request. Client {request.client}, method {request.method}, path {request.url.path}")
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(f"Request completed. status_code {response.status_code}, process_time={process_time:.2f}s")
        # Include the request ID in the response headers (optional)
        response.headers['X-Request-ID'] = request_id

    return response
