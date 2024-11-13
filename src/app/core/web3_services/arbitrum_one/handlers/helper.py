import hashlib
from typing import List, Dict, Any
from decimal import Decimal, ROUND_DOWN
from fastcrud import JoinConfig

from .....crud.crud_users import crud_users
from .....crud.crud_predictions import crud_predictions
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
    
async def get_admin_emails(db, schema: Any) -> List[str]:
    try:
        users = await crud_users.get_multi(
            db=db,
            schema_to_select=schema,
            is_admin=True
        )
        
        if users is None:
            raise Exception("Unable to fetch Administrators!")
        
        emails_list = [
            item['email']
            for item in users['data']
            if item.get('email') is not None
        ]
        
        return emails_list
    except Exception as e:
        logger.error(f"Failed to fetch admin details: {e}")
        return []

def fetch_addresses(data: Dict) -> List[str]:
    """
    Fetches the layer address and opponent addresses from the input dictionary,
    returning them as a plain list of addresses.

    Parameters:
        data (Dict): The dictionary containing betting data.

    Returns:
        List[str]: A list of addresses, with the layer address as the first element
                   followed by opponent addresses.
    """
    try:
       addresses = [data.get('layer')]

       # Add opponent addresses if they exist
       opponents = data.get('opponent', [])
       opponent_addresses = [opponent['opponent_address'] for opponent in opponents if 'opponent_address' in opponent]

       addresses.extend(opponent_addresses)

       return addresses
    except Exception as e:
        logger.error(f"Unknown Error Ocuured: {e}")

async def load_settled_prediction_data(
        db,
        pred_schema_to_select: Any,
        opponent_model: Any,
        pred_model: Any,
        opp_schema_to_select: Any,
        _hash_id: str
    ):
    """
    - Returns a dictionary of a prediction nested with opponent(s) data
    """
    try:
        preds = await crud_predictions.get_joined(
            db,
            schema_to_select=pred_schema_to_select,
            nest_joins=True,
            joins_config=[
                JoinConfig(
                    model=opponent_model,
                    join_on=pred_model.id == opponent_model.prediction_id,
                    schema_to_select=opp_schema_to_select,
                    relationship_type="one-to-many"
                )
            ],
            hash_identifier=_hash_id
        )
        if preds is None:
            raise Exception(f"Prediction Not found")
        else:
            return preds
    except Exception as e:
        logger.error(f"Unknown Error occured: {e}")