from beanie import Document
from fastapi import HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError, BulkWriteError
from loguru import logger
from motor.core import AgnosticClient


class CommonServices:
    def __init__(self, client: AgnosticClient):
        self.client = client

    def _initialize_document(self, document: Document, data: dict) -> Document:
        """Initializes a Beanie Document with provided data."""
        return document(**data)

    async def create_transaction(self, method, *args, **kwargs):
        """
        Handles the creation and execution of a transaction. 
        The method is a callable function that will be executed within a MongoDB transaction.
        """
        async def transaction(session=None):
            return await method(*args, **kwargs, session=session)

        # Manage the transaction
        return await self._manage_transaction(transaction)

    async def _manage_transaction(self, action_coroutine):
        """Manages the MongoDB transaction."""
        # Log the unique ID (memory address) of the MongoDB client
        logger.debug(f"Using MongoDB client with id: {id(self.client)}")

        # Start a session and log its unique ID
        async with await self.client.start_session() as session:
            logger.debug(f"Started session with id: {id(session)}")
            try:
                async with session.start_transaction():
                    logger.debug(
                        f"Transaction started with session id: {id(session)}")
                    result = await action_coroutine(session=session)
                    logger.debug(
                        f"Transaction successfully committed with session id: {id(session)}")
                    return result
            except BulkWriteError as e:
                error_message = "; ".join(
                    err['errmsg'] for err in e.details.get('writeErrors', []))
                logger.error(
                    f"Bulk write error: {e} | Details: {error_message}")
                raise HTTPException(status_code=500, detail=error_message)
            except DuplicateKeyError as e:
                logger.error(f"Duplicate key error: {e}")
                raise HTTPException(
                    status_code=400, detail='Duplicate key error')
            except WriteError as e:
                logger.error(f"Write error: {e}")
                if 'notNull' in str(e):
                    raise HTTPException(
                        status_code=400, detail='NotNullViolationError')
                raise HTTPException(status_code=500, detail='Write error')
            except PyMongoError as e:
                logger.error(f"MongoDB error: {e}")
                raise HTTPException(
                    status_code=500, detail='Unhandled MongoDB error')
            except Exception as e:
                # Loguru's exception method
                logger.exception(f"Unhandled exception in transaction: {e}")
                raise HTTPException(status_code=500, detail=str(e))
