from eth_abi.abi import decode

from app.core.logger import logging
from app.core.web3_services.arbitrum_one.handlers.helper import usdt_to_decimal, get_admin_emails
from app.core.akabokisi.manager import MailboxManager
from app.core.constants import (
    revenue_alert,
    admin_added_alert,
    admin_removed_alert,
    charge_fees_changed_alert,
    address_added_to_whiteliist_alert,
    address_removed_from_whiteliist_alert,
    ownership_transfer_initiation_alert,
    ownership_transfer_completed_alert
)
from app.core.akabokisi.messages import (
    on_revenue_withdrawal,
    on_admin_added,
    on_admin_removed,
    on_blacklist,
    on_fee_change,
    on_ownership_transfer_completion,
    on_ownership_transfer_initiation,
    on_whitlist,
)
from app.crud.crud_users import crud_users
from app.schemas.users import QuickAdminRead, QuickEmailRead

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

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_revenue_withdrawal(amount, public_address, mail_address)
        subject, queue_name = revenue_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'RevenueWithdrawn' event: {e}")

async def admin_added(payload, db):
    """
    Handler for `AdminAdded` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        _user: str = decode(['address'], payload['topics'][1])[0]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_admin_added(_user, _address)
        subject, queue_name = admin_added_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'AdminAdded' event: {e}")

async def admin_removed(payload, db):
    """
    Handler for `AdminRemoved` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        _user: str = decode(['address'], payload['topics'][1])[0]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_admin_removed(_user, _address)
        subject, queue_name = admin_removed_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'AdminRemoved' event: {e}")

async def fees_updated(payload, db):
    """
    Handler for `FeeChanged` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        _fee: int = decode(['uint256'], payload['topics'][1])[0]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_fee_change(_fee, _address)
        subject, queue_name = charge_fees_changed_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'FeeChanged' event: {e}")

async def updated_whitelist(payload, db):
    """
    Handler for `AddedToWhitelist` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        contract_address: str = decode(['address'], payload['topics'][1])[0]
        by: str = decode(['address'], payload['topics'][1])[1]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_whitlist(contract_address, _address, by)
        subject, queue_name = address_added_to_whiteliist_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'AddedToWhitelist' event: {e}")

async def updated_blacklist(payload, db):
    """
    Handler for `RemovedFromWhitelist` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        contract_address: str = decode(['address'], payload['topics'][1])[0]
        by: str = decode(['address'], payload['topics'][1])[1]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_blacklist(contract_address, _address, by)
        subject, queue_name = address_removed_from_whiteliist_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'RemovedFromWhitelist' event: {e}")

async def transfer_ownership_initiated(payload, db):
    """
    Handler for `OwnershipTransferInitiated` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        current_owner: str = decode(['address'], payload['topics'][1])[0]
        future_owner: str = decode(['address'], payload['topics'][1])[1]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_ownership_transfer_initiation(current_owner, future_owner, _address)
        subject, queue_name = ownership_transfer_initiation_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'OwnershipTransferInitiated' event: {e}")

async def transfer_ownership_completed(payload, db):
    """
    Handler for `OwnershipTransferCompleted` event

    Pushes notifications to queue.
    """
    try:
        _address: str = payload['address']
        previous_owner: str = decode(['address'], payload['topics'][1])[0]
        new_owner: str = decode(['address'], payload['topics'][1])[1]

        mail = MailboxManager()
        emails_list = await get_admin_emails(db, QuickAdminRead)
        message = on_ownership_transfer_completion(new_owner, previous_owner, _address)
        subject, queue_name = ownership_transfer_completed_alert()

        await mail.add_data_to_list(
            emails_list,
            queue_name,
            subject,
            message
        )
        
    except Exception as e:
        logger.error(f"Error processing 'OwnershipTransferCompleted' event: {e}")