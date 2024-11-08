import random
from decimal import Decimal, ROUND_DOWN
from eth_abi.abi import decode
from sqlalchemy import text
from asyncio import Lock
import asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import insert

from .....core.logger import logging
from .....models.user import Prediction
from .....crud.crud_predictions import crud_predictions
from .....crud.crud_users import crud_users
from .....crud.crud_opponent import crud_opponent
from .....crud.crud_matches import crud_matches
from .....schemas.opponents import OpponentCreate, QuickOppRead
from .....schemas.games import GameCreate, GameIdRead, GameStatusUpdate
from .....schemas.users import (
    UserRead,
    UpdateUserBalance,
    UserBalanceRead
)
from .....schemas.predictions import (
    PredictionCreate,
    OppPredUpdate,
    QuickPredRead,
    PredInitialUpdate,
    PredSettledUpdate,
    PredSoldUpdate,
    PredPriceUpdate
)
from .helper import generate_unique_id, usdt_to_decimal, validate_block_number

logger = logging.getLogger(__name__)

prediction_locks = {}
opponent_locks = {}


# ------usdtv1 handlers-----------------------
async def register_games(payload, db):
    """
    Handler for `GameRegistered` event

    Updates game model
    """
    try:
        _id: int = decode(['uint256'], payload['topics'][1])[0]

        game: GameIdRead | None = await crud_matches.get(
        db=db, schema_to_select=GameIdRead, match_id=_id
        )

        if game is None:
            await crud_matches.create(
                db,
                GameCreate(
                    match_id=_id,
                    resolved=False
                )
            )
            logger.info(f"New game registered: ID={_id}")
        else:
            logger.info(f"Game {_id} already registered!")
    except Exception as e:
        logger.error(f"Error processing 'GameRegistered' event: {e}")

async def game_resolved(payload, db):
    """
    Handler for `GameResolved` event

    Updates game model
    """
    try:
        _id: int = decode(['uint256'], payload['topics'][1])[0]

        game: GameIdRead | None = await crud_matches.get(
        db=db, schema_to_select=GameIdRead, match_id=_id
        )
        if game is None:
            raise Exception(f"Game ID {_id} not found")

        await crud_matches.update(
            db,
            GameStatusUpdate(
                resolved=True
            ),
            match_id=_id
        )
        logger.info(f"Game Resolved: ID={_id}")
    except Exception as e:
        logger.error(f"Error processing 'GameResolved' event: {e}")

async def process_usdtv1_deposits(payload, db, max_retries=3, retry_delay=0.1):
    """
    Handler for 'Deposited' event.
    Atomically updates user balance.
    """
    try:
        block_number: int = payload['blockNumber']
        src: str = decode(['address'], payload['topics'][1])[0]
        amount: int = decode(['uint256'], payload['topics'][2])[0]
        public_address = src.lower()

        wallet: UserBalanceRead | None = await crud_users.get(
            db=db, schema_to_select=UserBalanceRead, public_address=public_address
        )
        if wallet is None:
            raise Exception(f"User {public_address} not found")

        bn_list = validate_block_number(
            wallet['prev_block_number'],
            wallet['latest_block_number'],
            block_number
        )

        _prev = bn_list[0]
        _latest = bn_list[1]
        converted_amount = usdt_to_decimal(amount)

        for attempt in range(max_retries):
            update_query = text("""
            UPDATE "user"
            SET balance = balance + :amount,
                prev_block_number = :prev_block,
                latest_block_number = :latest_block
            WHERE public_address = :public_address AND latest_block_number < :latest_block
            RETURNING balance
            """)

            result = await db.execute(
                update_query,
                {
                    "amount": converted_amount,
                    "public_address": public_address,
                    "prev_block": _prev,
                    "latest_block": _latest
                }
            )

            if result.rowcount > 0:
                logger.info(f"Processed deposit: src={public_address}, amount={converted_amount}")
                break
            else:
                logger.warning(f"Attempt {attempt + 1}: Concurrent modification for user {public_address}. Retrying...")
                await asyncio.sleep(retry_delay * (2 ** attempt) * random.uniform(0.8, 1.2))
        else:
            raise Exception(f"Balance update failed for user {public_address} after {max_retries} attempts.")
    except IntegrityError:
        logger.error(f"IntegrityError: possible duplicate deposit for {public_address}")
    except Exception as e:
        logger.error(f"Error Processing 'Deposited' event: {e}")



async def process_usdtv1_claims(payload, db, max_retries=3, retry_delay=0.1):
    """
    Handler for `Claimed` event.
    Updates user balance atomically.
    """
    try:
        block_number: int = payload['blockNumber']
        dst: str = decode(['address'], payload['topics'][1])[0]
        amount: int = decode(['uint256'], payload['topics'][2])[0]
        public_address = dst.lower()

        wallet: UserBalanceRead | None = await crud_users.get(
            db=db, schema_to_select=UserBalanceRead, public_address=public_address
        )
        if wallet is None:
            raise Exception(f"User {public_address} not found")

        # Determine the correct block numbers for atomic update
        bn_list = validate_block_number(
            wallet['prev_block_number'],
            wallet['latest_block_number'],
            block_number
        )
        _prev = bn_list[0]
        _latest = bn_list[1]

        converted_amount = usdt_to_decimal(amount)

        # Retry loop with exponential backoff and jitter
        for attempt in range(max_retries):
            try:
                update_query = text("""
                UPDATE "user"
                SET balance = balance - :amount,
                    prev_block_number = :prev_block,
                    latest_block_number = :latest_block
                WHERE public_address = :public_address AND latest_block_number < :latest_block
                RETURNING balance
                """)

                result = await db.execute(
                    update_query,
                    {
                        "amount": converted_amount,
                        "public_address": public_address,
                        "prev_block": _prev,
                        "latest_block": _latest
                    }
                )

                if result.rowcount > 0:
                    logger.info(f"Processed claim: dst={public_address}, amount={converted_amount}")
                    break
                else:
                    logger.warning(f"Concurrent modification detected for user {public_address}. Retrying...")
                    await asyncio.sleep(retry_delay * (2 ** attempt) * random.uniform(0.8, 1.2))  # Exponential backoff with jitter

            except IntegrityError:
                logger.error(f"Integrity error during balance update for user {public_address}, attempt {attempt + 1}")
                await asyncio.sleep(retry_delay * (2 ** attempt) * random.uniform(0.8, 1.2))  # Exponential backoff with jitter
        else:
            raise Exception(f"Balance update failed for user {public_address} after {max_retries} attempts.")

    except Exception as e:
        logger.error(f"Error processing 'Claimed' event: {e}")


async def process_usdtv1_lays(payload, db):
    '''
    Handler for `Predicted` event.

    Adds Prediction to database.
    '''
    try:
        _address: str = payload['address']
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        layer: str = decode(['address'], payload['topics'][2])[0]
        gameid: int = decode(['uint256'], payload['topics'][3])[0]
        non_indexed_data = decode(["uint256", "uint256"], payload['data'])
        lay_amount: int = non_indexed_data[0]
        result: int = non_indexed_data[1]
        
        public_address = layer.lower()
        _contract_address = _address.lower()
        hash_id = generate_unique_id(bet_id, gameid, _contract_address)
        _key = (bet_id, gameid, _contract_address)

        wallet: UserRead | None = await crud_users.get(
            db=db, schema_to_select=UserRead, public_address=public_address
        )

        if wallet is None:
            raise Exception(f"User {public_address} not found")
        
        converted_amount = usdt_to_decimal(lay_amount)

        # Use the ON CONFLICT upsert to avoid duplicate entries
        stmt = insert(Prediction).values(
            user_id=wallet['id'],
            index=bet_id,
            layer=layer,
            hash_identifier=hash_id,
            match_id=gameid,
            contract_address=_contract_address,
            result=result,
            amount=converted_amount
        ).on_conflict_do_nothing(index_elements=['hash_identifier'])
        
        result = await db.execute(stmt)
        await db.commit()

        if result.rowcount == 0:
            logger.warning(f"Duplicate detected and ignored for {_key}")
        else:
            logger.info(f"Processed Lay: {_key}")
    
    except IntegrityError:
        logger.error(f"Duplicate prediction detected for Index={bet_id} and Game ID={gameid}")
    except Exception as e:
        logger.error(f"Error Processing 'Predicted' event: {e}")


async def process_usdtv1_backs(payload, db):
    """
    Handler for `Backed` event.

    Creates new `Opponent` and updates existing `Prediction` with atomic increment.
    """
    try:
        # Decode and prepare data
        _address: str = payload['address']
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        backer: str = decode(['address'], payload['topics'][2])[0]
        gameid: int = decode(['uint256'], payload['topics'][3])[0]
        non_indexed_data = decode(["uint256", "uint256"], payload['data'])
        back_amount: int = non_indexed_data[0]
        result: int = non_indexed_data[1]
        block_number: int = payload['blockNumber']

        public_address = backer.lower()
        _contract_address = _address.lower()
        hash_id = generate_unique_id(bet_id, gameid, _contract_address)


        # Check for duplicate back registration by `block_number`
        opp = await crud_opponent.get(
            db=db,
            schema_to_select=QuickOppRead,
            match_id=gameid,
            prediction_index=bet_id,
            opponent_address=public_address,
            block_number=block_number
        )
        if opp:
            raise Exception(f"Back already registered! Block_Number={block_number}")

        pred = await crud_predictions.get(
            db=db,
            schema_to_select=QuickPredRead,
            hash_identifier=hash_id
        )
        if pred is None:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid} from {_contract_address}")
        
        converted_amount = usdt_to_decimal(back_amount)

        # Create a new opponent entry
        await crud_opponent.create(
            db,
            OpponentCreate(
                prediction_id=pred['id'],
                match_id=gameid,
                prediction_index=bet_id,
                opponent_address=public_address,
                opponent_wager=converted_amount,
                result=result,
                block_number=block_number
            )
        )
        logger.info("Opponent Processed Successfully.")

        # Atomic update of total_opponent_wager
        update_query = text("""
        UPDATE prediction
        SET total_opponent_wager = total_opponent_wager + :amount,
            f_matched = CASE WHEN total_opponent_wager + :amount >= amount THEN true ELSE f_matched END,
            p_matched = true
        WHERE index = :bet_id AND match_id = :gameid AND contract_address = :contract_address
        RETURNING total_opponent_wager
        """)

        # Execute atomic increment update query
        result = await db.execute(
            update_query,
            {
                "amount": converted_amount,
                "bet_id": bet_id,
                "gameid": gameid,
                "contract_address": _contract_address
            }
        )

        if result.rowcount == 0:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid} from {_contract_address}")
        logger.info("Prediction Updated successfully.")
    except Exception as e:
        logger.error(f"Error Processing 'Backed' event: {e}")


async def process_usdtv1_bet_sell_initiated(payload, db):
    """
    Handler for `BetSellInitiated` event.

    Updates Prediction when a bet sale is initiated.
    """
    try:
        _address: str = payload['address']
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        gameid: int = decode(['uint256'], payload['topics'][2])[0]
        amount: int = decode(['uint256'], payload['topics'][3])[0]

        _contract_address = _address.lower()

        pred: QuickPredRead | None = await crud_predictions.get(
        db=db,
        schema_to_select=QuickPredRead,
        index=bet_id,
        match_id=gameid,
        contract_address=_contract_address
        )

        if pred is None:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid}")
        
        converted_amount = usdt_to_decimal(amount)
        await crud_predictions.update(
            db,
            PredInitialUpdate(
                for_sale=True,
                price=converted_amount
            ),
            index=bet_id,
            match_id=gameid,
            contract_address=_contract_address
        )
        logger.info("Prediction Updated successfully.")
    except Exception as e:
        logger.error(f"Error Processing 'BetsellInitiated' event: {e}")

async def process_usdtv1_selling_price_changed(payload, db):
    """
    Handler for `SellingPriceChanged` event.

    Updates Prediction when a bet selling price  is changed.
    """
    try:
        _address: str = payload['address']
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        gameid: int = decode(['uint256'], payload['topics'][2])[0]
        new_amount: int = decode(['uint256'], payload['topics'][3])[0]

        _contract_address = _address.lower()

        pred: QuickPredRead | None = await crud_predictions.get(
        db=db,
        schema_to_select=QuickPredRead,
        index=bet_id,
        match_id=gameid,
        contract_address=_contract_address
        )

        if pred is None:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid}")
        
        converted_amount = usdt_to_decimal(new_amount)
        await crud_predictions.update(
            db,
            PredPriceUpdate(
                price=converted_amount
            ),
            index=bet_id,
            match_id=gameid,
            contract_address=_contract_address
        )
        logger.info("Prediction Updated successfully.")
    except Exception as e:
        logger.error(f"Error Processing 'SellingPriceChanged' event: {e}")

async def process_usdtv1_bet_sold(payload, db):
    """
    Handler for `BetSold` event.

    Updates Prediction when a bet sale is bought.
    """
    try:
        _address: str = payload['address']
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        gameid: int = decode(['uint256'], payload['topics'][2])[0]
        buyer: str = decode(['address'], payload['topics'][3])[0]
        public_address = buyer.lower()
        _contract_address = _address.lower()

        pred: QuickPredRead | None = await crud_predictions.get(
        db=db,
        schema_to_select=QuickPredRead,
        index=bet_id,
        match_id=gameid,
        contract_address=_contract_address
        )

        if pred is None:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid}")
        
        await crud_predictions.update(
            db,
            PredSoldUpdate(
                layer=public_address
            ),
            index=bet_id,
            match_id=gameid,
            contract_address=_contract_address
        )
        logger.info("Prediction Updated successfully.")
    except Exception as e:
        logger.error(f"Error Processing 'BetSold' event: {e}")

async def process_usdtv1_settled_pred(payload, db):
    """
    Handler for `PredictionSettled` event.

    Updates Prediction when a bet is settled.
    """
    try:
        _address: str = payload['address']
        bet_id: int = decode(['uint256'], payload['topics'][1])[0]
        gameid: int = decode(['uint256'], payload['topics'][2])[0]

        _contract_address = _address.lower()

        pred: QuickPredRead | None = await crud_predictions.get(
        db=db,
        schema_to_select=QuickPredRead,
        index=bet_id,
        match_id=gameid,
        contract_address=_contract_address
        )

        if pred is None:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid}")
        
        await crud_predictions.update(
            db,
            PredSettledUpdate(
                settled=True
            ),
            index=bet_id,
            match_id=gameid,
            contract_address=_contract_address
        )
        logger.info("Prediction Updated successfully.")
    except Exception as e:
        logger.error(f"Error Processing 'PredictionSettled' event: {e}")