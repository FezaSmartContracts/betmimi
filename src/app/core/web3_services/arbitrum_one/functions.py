import asyncio

from ....core.logger import logging
from ..utils import arbitrum_contract_addresses
from .callbacks import process_arbitrum_callbacklogs

logger = logging.getLogger(__name__)


async def init_subscribe_to_arb_events(subs_handler):
    "Initiates Event subscription for event Logs"
    try:
        CONTRACT_ADDRESSES = arbitrum_contract_addresses()
        _event_type = "logs"

        while not subs_handler.is_connected():
            logger.info("Websocket Not Connected Yet!")
            await asyncio.sleep(5)
        logger.info("Websocket is sucessfully Connected!")

        await subs_handler.subscribe(
            process_arbitrum_callbacklogs,
            _event_type,
            address=CONTRACT_ADDRESSES
        )
        logger.info(f"Successfully Subscribed to USDT(arbitrum) event {_event_type}")

    except Exception as e:
        logger.error(f"Failed to subscribe to events: {e}")
    except asyncio.TimeoutError:
        logger.error("Not subscribed to events: Time Out!")
    except asyncio.CancelledError:
        logger.error("Event subscripion process Cancelled!")