import asyncio
import signal
from web3_services.manager import WebSocketManager
from app.core.logger import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

alchemy_arb_uri: str = f"wss://arb-sepolia.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"

async def main():
    ws_manager = WebSocketManager(alchemy_arb_uri, "arb_alchemy_logs_queue")
    await ws_manager.start_processing()

    try:
        while True:
            await asyncio.sleep(2)
    except asyncio.CancelledError:
        logger.info("Gracefully shutting down WebSocket manager...")
        await ws_manager.shutdown()

async def shutdown(loop, ws_task):
    """Initiates a graceful shutdown."""
    logger.info("Received shutdown signal.")
    ws_task.cancel()
    await ws_task  # Allow main() to handle its cleanup
    loop.stop()

def setup_signal_handlers(loop, ws_task):
    loop.add_signal_handler(signal.SIGINT, lambda: asyncio.create_task(shutdown(loop, ws_task)))
    loop.add_signal_handler(signal.SIGTERM, lambda: asyncio.create_task(shutdown(loop, ws_task)))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    ws_task = loop.create_task(main())
    setup_signal_handlers(loop, ws_task)

    try:
        loop.run_forever()
    finally:
        loop.close()
