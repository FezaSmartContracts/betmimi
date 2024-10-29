from typing import Dict, Annotated
from decimal import Decimal, ROUND_DOWN
from hexbytes import HexBytes
from eth_abi.abi import decode
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..utils import load_abi, get_event_topic
from ....core.db.database import async_get_db
from ....core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ....core.logger import logging
from ....crud.crud_predictions import crud_predictions
from ....crud.crud_users import crud_users
from ....crud.crud_opponent import crud_opponent
from ....schemas.users import (
    UserRead,
    UpdateUserBalance,
    UserUpdateInternal,
    UserBalanceRead
)
from ....schemas.predictions import (
    PredictionCreate,
    PredictionRead,
    QuickPredRead,
    PredictionUpdate,
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
    Opponent
)
logger = logging.getLogger(__name__)

ABI_PATH = "../artifacts/arbitrum/USDTv1.json"

def usdtv1_event_topics_dict() -> Dict[str, HexBytes]:
    """Constructs a dictionary of event topics for USDTv1 events."""
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
        logger.error(f"Failed to construct event topics dictionary: {e}")
        return {}

def usdtv1_event_handlers() -> Dict[str, callable]:
    """Maps events to their respective handler functions."""
    return {
        "Deposited": process_usdtv1_deposits,
        "Predicted": process_usdtv1_lays,
        "Backed": process_usdtv1_backs
    }



# ------usdtv1 handlers-----------------------
async def process_usdtv1_deposits(payload, db):
    """
    Handler for 'Deposited' event.

    Updates user balance.
    """
    try:
        src: str = decode(['address'], payload['topics'][1])[0]
        amount: int = decode(['uint256'], payload['topics'][2])[0]
        public_address = src.lower()

        wallet: UserBalanceRead | None = await crud_users.get(
        db=db, schema_to_select=UserBalanceRead, public_address=public_address
        )

        if wallet is None:
            raise Exception(f"User {public_address} not found")
        
        current_balance = wallet['balance']
        converted_amount = (Decimal(amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT

        current_balance += converted_amount
        await crud_users.update(
            db,
            UpdateUserBalance(
                balance=current_balance
            )
        )
        
        logger.info(f"Processed deposit: src={public_address}, amount={amount}")
    except Exception as e:
        logger.error(f"Error processing 'Deposited' event: {e}")


async def process_usdtv1_lays(payload, db):
    """
    Handler for 'Predicted' event.

    Adds Prediction to database.
    """
    try:
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        layer: str = decode(['address'], payload['topics'][2])[0]
        gameid: int = decode(['uint256'], payload['topics'][3])[0]
        non_indexed_data = decode(["uint256", "uint256"], payload['data'])
        lay_amount: int = non_indexed_data[0]
        result: int = non_indexed_data[1]

        public_address = layer.lower()

        wallet: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, public_address=public_address
        )

        if wallet is None:
            raise Exception(f"User {public_address} not found")
        
        converted_amount = (Decimal(lay_amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
        await crud_predictions.create(
            db,
            PredictionCreate(
                user_id=wallet['id'],
                index=bet_id,
                layer=layer,
                match_id=gameid,
                result=result,
                amount=converted_amount
            )
        )
        logger.info(f"Processed Lay: layer={public_address}")
    except Exception as e:
        logger.error(f"Error Processing 'Predicted' event: {e}")

async def process_usdtv1_backs(payload, db):
    """
    Handler for `Backed` event.

    Creates new `Opponent` and updates existing `Prediction`.
    """
    try:
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        backer: str = decode(['address'], payload['topics'][2])[0]
        gameid: int = decode(['uint256'], payload['topics'][3])[0]
        non_indexed_data = decode(["uint256", "uint256"], payload['data'])
        back_amount: int = non_indexed_data[0]
        result: int = non_indexed_data[1]

        public_address = backer.lower()

        pred: QuickPredRead | None = await crud_predictions.get(
        db=db, schema_to_select=QuickPredRead, index=bet_id, match_id=gameid
        )

        if pred is None:
            logger.error(f"No prediction of index {bet_id} for Game: {gameid}")
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid}")
        
        converted_amount = (Decimal(back_amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
        await crud_opponent.create(
            OpponentCreate(
                db,
                prediction_id=pred['id'],
                match_id=gameid,
                prediction_index=bet_id,
                opponent_address=public_address,
                opponent_wager=converted_amount,
                result=result
            )
        )
        logger.info("Opponent Processed Successfully.")

        prev_wager = pred['total_opponent_wager']
        new_wager = prev_wager + converted_amount
        if new_wager >= pred['amount']:
            bol = True
        else:
            bol = False

        await crud_predictions(
            PredictionUpdate(
                db,
                total_opponent_wager=new_wager,
                f_matched=bol,
                p_matched=True,
            )
        )
        logger.info("Prediction Updated successfully.")
    except Exception as e:
        logger.error(f"Error Processing 'Backed' event: {e}")