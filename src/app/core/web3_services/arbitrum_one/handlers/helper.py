import asyncio
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy import text

from .....models.user import Prediction
from .....core.logger import logging

logger = logging.getLogger(__name__)

def generate_unique_id(bet_id: int, match_id: int, contract_address: str) -> str:
    unique_string = f"{bet_id}_{match_id}_{contract_address}"
    unique_hash = hashlib.sha256(unique_string.encode()).hexdigest()
    return unique_hash

