from beanie import PydanticObjectId, Document
from fastapi import HTTPException
from pymongo.errors import PyMongoError, DuplicateKeyError, WriteError, BulkWriteError

class CommonServices:
    def __init__(self, client):
        self.client = client

    def _initialize_document(self, document: Document, data:dict) -> Document:
        return document(**data)

    async def create_transaction(self, method, *args, **kwargs):
        async def transaction(session=None):
            return await method(session=session, *args, **kwargs)
        return await self._manage_transaction(transaction)

    async def _manage_transaction(self, action_coroutine):
        session = await self.client.start_session()
        try:
            async with session.start_transaction():
                result = await action_coroutine(session=session)
                return result
        except PyMongoError as e:
            print(f"Handling MongoDB error: {e}")
            if isinstance(e, BulkWriteError) and 'writeErrors' in e.details:
                error_message = "; ".join(err['errmsg'] for err in e.details['writeErrors'])
                raise HTTPException(status_code=500, detail=error_message)
            elif isinstance(e, DuplicateKeyError):
                raise HTTPException(status_code=400, detail='Duplicate key error')
            elif isinstance(e, WriteError) and 'notNull' in str(e):
                raise HTTPException(status_code=400, detail='NotNullViolationError')
            else:
                raise HTTPException(status_code=500, detail='Unhandled MongoDB error')
        except HTTPException as e:
            raise  # Simply propagate the original HTTPException without modification
        except Exception as e:
            print(f"Unhandled exception in transaction: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            await session.end_session()
