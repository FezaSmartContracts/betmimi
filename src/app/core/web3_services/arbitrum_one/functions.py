import asyncio

from ....core.logger import logging
from ..utils import arbitrum_contract_addresses
from .callbacks import process_arbitrum_callbacklogs
from ..fallback_manager import FallBackSubscriptionHandler
from ...config import settings
from ..strings import ALCHEMY_REDIS_QUEUE_NAME, ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME

logger = logging.getLogger(__name__)

CONTRACT_ADDRESSES = arbitrum_contract_addresses()
AL = ALCHEMY_REDIS_QUEUE_NAME
AS = ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME
_event_type = "logs"

async def init_subscribe_to_arb_events(subs_handler):
    "Initiates Event subscription for event Logs"
    try:
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

async def queue_missed_events_for_usdtv1_arb_alchemy(
        from_block: int,
        to_block: int
    ) -> None:
    """
    Subscribes to events filtered by the `from_block` to the `to_block`
    """
    filter_params = {
        "address": CONTRACT_ADDRESSES,
        "fromBlock": from_block,
        "toBlock": to_block
    }
    WSS_URL = f"{settings.ALCHEMY_BASE_WSS_URI}{settings.ALCHEMY_API_KEY}"
    try:
        manager = FallBackSubscriptionHandler(WSS_URL, AL, AS)

        await manager.fetch_logs(
            process_arbitrum_callbacklogs,
            filter_params
        )
        while not manager.is_connected():
            logger.info("Fallback Websocket Not Connected Yet!")
            await asyncio.sleep(5)
        logger.info("Fallback Websocket is sucessfully Connected!")
        
        logger.info(f"Ready to receive event logs!")

    except Exception as e:
        logger.error(f"Failed to subscribe to fallback events: {e}")