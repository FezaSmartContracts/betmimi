import asyncio

from app.core.logger import logging
from app.core.web3_services.utils import arbitrum_contract_addresses
from app.core.web3_services.arbitrum_one.callbacks import process_arbitrum_callbacklogs
from app.core.web3_services.fallback_manager import FallBackSubscriptionHandler
from app.core.config import settings
from app.core.constants import (
    ALCHEMY_REDIS_QUEUE_NAME,
    ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME
)

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
    manager = FallBackSubscriptionHandler(WSS_URL, AL, AS)

    try:
        # Apply timeout to the entire connection and log-fetching process
        await asyncio.wait_for(
            manager.fetch_logs(process_arbitrum_callbacklogs, filter_params),
            timeout=float(settings.WEBSOCKET_TIMEOUT)
        )

        # Connection check with a timeout loop
        while not manager.is_connected():
            logger.info("Fallback WebSocket Not Connected Yet!")
            await asyncio.sleep(5)
        
    except asyncio.TimeoutError:
        logger.error("WebSocket operation timed out.")
        await manager.disconnect()
    except asyncio.CancelledError:
        logger.error("Task was canceled, disconnecting WebSocket...")
        await manager.disconnect()
        raise 
    except Exception as e:
        logger.error(f"Failed to subscribe to fallback events: {e}")
    finally:
        await manager.disconnect()
        logger.info("WebSocket disconnected.")
