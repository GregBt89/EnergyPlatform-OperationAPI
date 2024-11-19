import sys
from typing import Sequence, Type, TypeVar

from beanie import Document

# All database models must be imported here to be able to
# initialize them on startup.
from app.db.models.mCatalogs import *
from app.db.models.mMeasurements import *
from app.db.models.mPods import *
from app.db.models.mForecasts import (
    AssetForecast,
    PodForecast,
    MarketForecast
)
from app.db.models.mOptimization import *

DocType = TypeVar("DocType", bound=Document)



def gather_documents() -> Sequence[Type[DocType]]:
    """Returns a list of all MongoDB document models defined in `models` module."""
    from inspect import getmembers, isclass
    return [
        doc
        for _, doc in getmembers(sys.modules[__name__], isclass)
        if issubclass(doc, Document) and doc.__name__ != "Document"
    ]

