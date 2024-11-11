from eth_abi.abi import decode

from .....core.logger import logging
from .helper import generate_unique_id, usdt_to_decimal, validate_block_number
from ....akabokisi.manager import MailboxManager
from ....constants import REVENUE_WITHDRAW_ALERT
from ....akabokisi.messages import on_game_register, on_revenue_withdrawal
from .....crud.crud_users import crud_users
from .....schemas.users import (
    QuickAdminRead,
    QuickEmailRead,
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
        amount = usdt_to_decimal(_amount)

        caller: QuickEmailRead | None = crud_users.get(
            db=db,
            schema_to_select=QuickEmailRead,
            public_address=public_address
        )
        if caller is None:
            mail_address = f"UNKNOWN"
        else:
            mail_address = caller['email']

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

        mail = MailboxManager()
        message = on_revenue_withdrawal(amount, public_address, mail_address)

        await mail.add_data_to_list(
            emails_list,
            REVENUE_WITHDRAW_ALERT,
            "Revenue Withdrawn",
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'RevenueWithdrawn' event: {e}")
