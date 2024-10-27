import logging
from typing import Dict, Annotated
from hexbytes import HexBytes
from eth_abi.abi import decode
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..utils import load_abi, get_event_topic
from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....crud.crud_predictions import crud_predictions
from ....crud.crud_users import crud_users
from ....crud.crud_opponent import crud_opponent
from ....schemas.users import (
    UserRead,
    UserBalanceCreate,
    UserBalanceRead,
    UserBalanceUpdateInternal,
    UserBalanceUpdate,
    ReadUserBalance
)
from ....schemas.predictions import (
    PredictionCreate,
    PredictionRead,
    PredictionUpdateInternal
)
from ....schemas.opponents import (
    OpponentCreate,
    OpponentRead,
    OpponentUpdateInternal
)
from ....models.user import (
    User,
    Prediction,
    UserBalance,
    Opponent
)

ABI_PATH = "../artifacts/arbitrum/usdtv1.json"

def usdtv1_event_topics_dict() -> Dict[str, HexBytes]:
    """Constructs a dictionary of event topics for usdtv1 events."""
    try:
        ABI = load_abi(ABI_PATH)
        return {
            "Deposited": get_event_topic(ABI, "Deposited"),
            "Predicted": get_event_topic(ABI, "Predicted"),
            "Backed": get_event_topic(ABI, "Backed"),
            "Claimed": get_event_topic(ABI, "Claimed"),
            "GameRegistered": get_event_topic(ABI, "GameRegistered"),
            "GameResolved": get_event_topic(ABI, "GameResolved"),
            "PredictionSettled": get_event_topic(ABI, "PredictionSettled"),
            "ReceivedFallback": get_event_topic(ABI, "ReceivedFallback"),
            "BetSold": get_event_topic(ABI, "BetSold"),
            "BetSellInitiated": get_event_topic(ABI, "BetSellInitiated"),
            "SellingPriceChanged": get_event_topic(ABI, "SellingPriceChanged")
        }
    except Exception as e:
        logging.error(f"Failed to construct event topics dictionary: {e}")
        return {}

def usdtv1_event_handlers() -> Dict[str, callable]:
    """Maps events to their respective handler functions."""
    return {
        "Deposited": process_usdtv1_deposits,
        # Add additional handlers here
    }

async def process_usdtv1_deposits(
        payload,
        db: Annotated[AsyncSession, Depends(async_get_db)]
    ):
    """
    Handler for 'Deposited' event.

    Updates user balance.
    """
    try:
        src: str = decode(['address'], payload['topics'][1])[0]
        amount: int = decode(['uint256'], payload['topics'][2])[0]
        public_address = src.lower()

        wallet: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, public_address=public_address
        )
        if wallet is None:
            raise Exception(f"User {public_address} not found")
        
        user_balance: UserBalanceRead = await crud_users.get(
            db=db,
            schema_to_select=UserBalanceRead,
            return_as_model=True,
            one_or_none=True,
            user_id=wallet.id
        )
        if user_balance:
            user_balance.amount += amount
            await crud_users.update(
                db,
                UserBalanceUpdate(
                    amount=user_balance
                )
            )
        else:
            raise RuntimeError("No UserBalance table associated to user")
        
        logging.info(f"Processed deposit: src={public_address}, amount={amount}")
    except Exception as e:
        logging.error(f"Error processing 'Deposited' event: {e}")

