from fastapi import Query
from typing import Optional, Union
from datetime import datetime
from bson import ObjectId
from dataclasses import dataclass, asdict, fields
from app.validation.queries.vqBase import BaseQuery