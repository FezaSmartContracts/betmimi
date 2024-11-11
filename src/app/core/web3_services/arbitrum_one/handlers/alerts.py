from eth_abi.abi import decode

from .....core.logger import logging
from .helper import generate_unique_id, usdt_to_decimal, validate_block_number
from ....akabokisi.manager import MailboxManager
from ....constants import GAME_REGISTERED, PREDICTION_LAYED
from ....akabokisi.messages import on_game_register, on_lay
from .....crud.crud_users import crud_users
from .....schemas.users import (
    QuickAdminRead,
    UserBalanceRead,
    QuickUpdateUserBalance
)
from .....schemas.predictions import (
    QuickPredRead,
    PredInitialUpdate,
    PredSettledUpdate,
    PredSoldUpdate,
    PredPriceUpdate
)
logger = logging.getLogger(__name__)

async def revenue_withdrawn(payload, db):
    """
    Handler for `RevenueWithdrawn` event

    Pushes notifications to queue.
    """
    try:
        _user: str = decode(['address'], payload['topics'][1])[0]
        _amount: int = decode(['uint256'], payload['topics'][1])[1]

        public_address = _user.lower()

        users: QuickAdminRead | None = await crud_users.get_multi(
            db=db,
            schema_to_select=QuickAdminRead,
            return_as_model=True,
            public_address=public_address,
            is_admin=True
        )
        
        if users is None:
            raise Exception(f"Unable to fetch Admnistrators!")
        
        #emails_list = []
        #for item in users:
            #emails_list.append(item[2])

        
        #mail = MailboxManager()
        #message = on_game_register(_id)
        #await mail.add_data_to_list(["mosesmuwawu@gmail.com", "andersonixon12@gmail.com", "dearjovic@gmail.com"], GAME_REGISTERED, "New Game Registered", message)
        
    except Exception as e:
        logger.error(f"Error processing 'GameRegistered' event: {e}")
