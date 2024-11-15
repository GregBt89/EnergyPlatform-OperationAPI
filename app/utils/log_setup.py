from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import sys
import time
import traceback
import uuid
import contextvars
from loguru import logger


# Create a context variable to store the request ID (UUID)
request_id_context = contextvars.ContextVar("request_id", default=None)

# Define a log format that includes the request ID (UUID)
log_format = "<green>{time}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | {message} | <yellow>{extra[request_id]}</yellow>"

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
        info = f"New request. Client {request.client}, method {request.method}, path {request.url.path}"
        if request.url.query:
            info += f", {request.url.query}"
        logger.info(info)
        start_time = time.time()
        try:
            # Process the request and get the response
            response = await call_next(request)

            process_time = time.time() - start_time
            logger.info(
                f"Request completed. status_code={response.status_code}, process_time={process_time:.2f}s"
            )

            # Include the request ID in the response headers
            response.headers["X-Request-ID"] = request_id
            return response

        except HTTPException as exc:
            # Handle HTTP exceptions
            process_time = time.time() - start_time
            logger.warning(
                f"HTTPException raised. status_code={exc.status_code}, detail={exc.detail}, process_time={process_time:.2f}s"
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": exc.detail,
                    "request_id": request_id,
                },
            )

        except Exception as exc:
            # Handle other unhandled exceptions
            process_time = time.time() - start_time
            # Log full exception details
            exc_type = type(exc).__name__
            exc_message = str(exc)
            exc_traceback = traceback.format_exc()

            logger.error(
                f"Unhandled exception occurred. status_code=500, process_time={process_time:.2f}s\n"
                f"Exception Type: {exc_type}\n"
                f"Exception Message: {exc_message}\n"
                f"Traceback: {exc_traceback}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "An internal server error occurred.",
                    "request_id": request_id,
                },
            )
