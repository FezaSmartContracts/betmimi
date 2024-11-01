import asyncio
import signal
from web3_services.manager import SubscriptionHandler
from app.core.logger import logging
from app.core.config import settings

from .functions import init_subscribe_to_arb_events

logger = logging.getLogger(__name__)

alchemy_arb_uri: str = f"wss://arb-sepolia.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"
redis_queue_name = "arb_alchemy_logs_queue"
subscriptions_queue_name = "subscriptions_queue"

async def main():
    handler = SubscriptionHandler(
        alchemy_arb_uri,
        redis_queue_name,
        subscriptions_queue_name
    )

    async def shutdown():
        logger.info("Shutting down gracefully...")
        await handler._cleanup_subscriptions()
        logger.info("Unsubscribed from all events. Exiting...")

    # Handle shutdown signals
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    # Run subscriptions and event initialization concurrently
    await asyncio.gather(
        handler.process_subscriptions(),
        init_subscribe_to_arb_events(handler)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Application stopped by user or system.")
