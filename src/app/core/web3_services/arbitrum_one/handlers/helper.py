import hashlib
from typing import List
from decimal import Decimal, ROUND_DOWN

from .....schemas.users import QuickAdminRead 
from .....crud.crud_users import crud_users
from .....core.logger import logging

logger = logging.getLogger(__name__)

def generate_unique_id(bet_id: int, match_id: int, contract_address: str) -> str:
    """Generates a unique Hash for specific element inputs"""
    unique_string = f"{bet_id}_{match_id}_{contract_address}"
    unique_hash = hashlib.sha256(unique_string.encode()).hexdigest()
    return unique_hash

def usdt_to_decimal(value: int) -> Decimal:
    """Converts amount from on-chain to a human readable format in USDT"""
    return (Decimal(value) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)

def validate_block_number(prev_block_number: int, latest_block_number: int, block_number: int) -> List[int]:
    """
    Validates block number uniqueness to avoid duplicate deposits

    Returns a list of previous and latest block numbers
    """
    if prev_block_number or latest_block_number != block_number:
        if block_number < latest_block_number:
            _prev = block_number
            _latest = latest_block_number
            return [_prev, _latest]
        else:
            _prev = latest_block_number
            _latest = block_number
            return [_prev, _latest]
    else:
        raise Exception(f"Deposit at {block_number} is already registered!")
    
async def get_admin_emails(db) -> List[str]:
    try:
        users: QuickAdminRead | None = await crud_users.get_multi(
            db=db,
            schema_to_select=QuickAdminRead,
            is_admin=True
        )
        
        if users is None:
            raise Exception(f"Unable to fetch Admnistrators!")
        
        emails_list = []
        for item in users['data']:
            if item['email'] != None:
                emails_list.append(item['email'])
            else:
                continue
    except Exception as e:
        logger.error("Failed to fetch admin details")

