import asyncio
import signal
from app.core.web3_services.manager import SubscriptionHandler
from app.core.logger import logging
from app.core.config import settings
from app.core.constants import ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME, ALCHEMY_REDIS_QUEUE_NAME

from .functions import init_subscribe_to_arb_events

logger = logging.getLogger(__name__)

alchemy_arb_uri: str = f"{settings.ALCHEMY_BASE_WSS_URI}{settings.ALCHEMY_API_KEY}"
redis_queue_name = ALCHEMY_REDIS_QUEUE_NAME
subscriptions_queue_name = ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME

class WebSocketMonitor:
    def __init__(self):
        """Monitors and Manages websocket connections"""
        self.alchemy_arb_uri = f"{settings.ALCHEMY_BASE_WSS_URI}{settings.ALCHEMY_API_KEY}"
        self.redis_queue_name = ALCHEMY_REDIS_QUEUE_NAME
        self.subscriptions_queue_name = ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME
        self.handler = SubscriptionHandler(
            self.alchemy_arb_uri,
            self.redis_queue_name,
            self.subscriptions_queue_name
        )

    async def start(self):
        """Start the WebSocket monitoring process."""

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        # Run tasks concurrently
        try:
            await asyncio.gather(
                self.handler.process_subscriptions(),
                init_subscribe_to_arb_events(self.handler)
            )
        except Exception as e:
            logger.error(f"Error occurred in WebSocketMonitor: {e}")
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Gracefully shut down the WebSocket monitor, releasing resources."""
        logger.info("Shutting down WebSocket monitor gracefully...")
        await self.handler._cleanup_subscriptions()
        logger.info("Unsubscribed from all events. Exiting...")