from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from fastapi import HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError, BulkWriteError
from loguru import logger
from motor.core import AgnosticClient
from typing import List
from bson import ObjectId


class CommonServices:
    def __init__(self, client: AgnosticClient):
        self.client = client

    @staticmethod
    def _to_ObjectId(_id):
        if ObjectId.is_valid(_id):
            return ObjectId(_id)
        raise ValueError(f"ID {_id} not a valid ObjectID")

    @staticmethod
    def _to_list(x):
        return [x] if not isinstance(x, list) else x

    async def _non_existing_ids(self, models: List[BaseModel], field: str, doc: Document):
        # Extract all asset_ids from the measurements
        model_ids = {PydanticObjectId(getattr(model, field))
                     for model in self._to_list(models)}

        existing_docs = await doc.all()
        existing_docs_id = {doc.id for doc in existing_docs}

        return sorted(model_ids - existing_docs_id)

    def _initialize_document(self, document: Document, data: dict) -> Document:
        """Initializes a Beanie Document with provided data."""
        try:
            return document(**data)
        except Exception as e:
            msg = f"Exception occured at {document} initilization: {str(e)}"
            logger.error(msg)
            raise HTTPException(
                status_code=500,
                detail=msg
            )

    async def create_transaction(self, method, *args, **kwargs):
        """
        Handles the creation and execution of a transaction. 
        The method is a callable function that will be executed within a MongoDB transaction.
        """
        async def transaction(session=None):
            kwargs.update({"session": session})
            return await method(*args, **kwargs)

        # Manage the transaction
        return await self._manage_transaction(transaction)

    async def _manage_transaction(self, action_coroutine):
        """Manages the MongoDB transaction."""
        # Log the unique ID (memory address) of the MongoDB client
        logger.debug(f"Using MongoDB client with id: {id(self.client)}")
        logger.debug(action_coroutine)
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
