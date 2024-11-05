from decimal import Decimal, ROUND_DOWN
from eth_abi.abi import decode

from .....core.logger import logging
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


logger = logging.getLogger(__name__)


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


async def process_usdtv1_deposits(payload, db):
    """
    Handler for 'Deposited' event.

    Updates user balance.
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
        
        # WARNING: The shear effectiveness of the following implementation is highly dependent
        # on the quicker reactions of the team to Websocket disconnections!
        # NOTE: this isn't an efficient Implementation. Should be strictly changed in the future.
        # The aim here is to ensure that one's balance isn't updated more than once from the same event log
        if wallet['prev_block_number'] or wallet['latest_block_number'] != block_number:
            if block_number < wallet['latest_block_number']:
                _prev = block_number
                _latest = wallet['latest_block_number']
            else:
                _prev = wallet['latest_block_number']
                _latest = block_number
        else:
            raise Exception(f"Deposit at {block_number} is already registered!")
        
        current_balance = wallet['balance']
        converted_amount = (Decimal(amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT

        current_balance += converted_amount
        await crud_users.update(
            db,
            UpdateUserBalance(
                balance=current_balance,
                prev_block_number=_prev,
                latest_block_number=_latest
            ),
            public_address=public_address
        )
        
        logger.info(f"Processed deposit: src={public_address}, amount={converted_amount}")
    except Exception as e:
        logger.error(f"Error processing 'Deposited' event: {e}")

async def process_usdtv1_claims(payload, db):
    """
    Handler for `Claimed` event.

    Updates user balance.
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
        
        # WARNING: The shear effectiveness of the following implementation is highly dependent
        # on the quicker reactions of the team to Websocket disconnections!
        # NOTE: this isn't an efficient Implementation. Should be strictly changed in the future.
        # The aim here is to ensure that one's balance isn't updated more than once from the same event log
        if wallet['prev_block_number'] or wallet['latest_block_number'] != block_number:
            if block_number < wallet['latest_block_number']:
                _prev = block_number
                _latest = wallet['latest_block_number']
            else:
                _prev = wallet['latest_block_number']
                _latest = block_number
        else:
            raise Exception(f"Deposit at {block_number} is already registered!")
        
        current_balance = wallet['balance']
        converted_amount = (Decimal(amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
        current_balance -= converted_amount

        await crud_users.update(
            db,
            UpdateUserBalance(
                balance=current_balance
            ),
            public_address=public_address,
            prev_block_number=_prev,
            latest_block_number=_latest
        )
        
        logger.info(f"Processed withdraw: dst={public_address}, amount={converted_amount}")
    except Exception as e:
        logger.error(f"Error processing 'Claimed' event: {e}")

async def process_usdtv1_lays(payload, db):
    """
    Handler for `Predicted` event.

    Adds Prediction to database.
    """
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

        wallet: UserRead | None = await crud_users.get(
        db=db, schema_to_select=UserRead, public_address=public_address
        )

        if wallet is None:
            raise Exception(f"User {public_address} not found")
        
        # ensure prediction is only registered once
        pred: QuickPredRead | None = await crud_predictions.get(
            db=db,
            schema_to_select=QuickPredRead,
            index=bet_id,
            match_id=gameid,
            contract_address=_contract_address
        )
        if pred:
            raise Exception(f"Prediction Index={bet_id} and ID={gameid} already registered")
        
        converted_amount = (Decimal(lay_amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
        await crud_predictions.create(
            db,
            PredictionCreate(
                user_id=wallet['id'],
                index=bet_id,
                layer=layer,
                match_id=gameid,
                contract_address=_contract_address,
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

        # ensures a single back isn't added more than once. Here, the most important filter is `block_number`.
        # It's possible for anything to go wrong incase a single user makes more than one back to a given prediction within
        # a period of 0.25s(arbitrum ones's block age). Practically, there is a chance of 1/1,000,000 for this to happen.
        opp: QuickOppRead | None = await crud_opponent.get(
            db=db,
            schema_to_select=QuickOppRead,
            match_id=gameid,
            prediction_index=bet_id,
            opponent_address=public_address,
            block_number=block_number
        )
        if opp:
            raise Exception(f"Back already registered! Block_Number={block_number}")

        pred: QuickPredRead | None = await crud_predictions.get(
        db=db,
        schema_to_select=QuickPredRead,
        index=bet_id,
        match_id=gameid,
        contract_address=_contract_address
        )

        if pred is None:
            raise Exception(f"No prediction of index {bet_id} for Game: {gameid} from {_contract_address}")
        
        converted_amount = (Decimal(back_amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
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

        prev_wager = pred['total_opponent_wager']
        new_wager = prev_wager + converted_amount
        if new_wager >= pred['amount']:
            bol = True
        else:
            bol = False

        await crud_predictions.update(
            db,
            OppPredUpdate(
                total_opponent_wager=new_wager,
                f_matched=bol,
                p_matched=True
            ),
            index=bet_id,
            match_id=gameid,
            contract_address=_contract_address
        )
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
        
        converted_amount = (Decimal(amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
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
        
        converted_amount = (Decimal(new_amount) / Decimal(10**6)).quantize(Decimal("0.01"), rounding=ROUND_DOWN) # USDT
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