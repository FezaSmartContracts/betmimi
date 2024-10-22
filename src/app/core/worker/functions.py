import asyncio
import logging

import uvloop
from arq.worker import Worker

from ...core.web3_services.manager import ContractWebSocketManager

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    return f"Task {name} is complete!"

async def subscribe_to_events(ctx: Worker, name: str) -> str:
    logging.info(f"Starting WebSocket subscription for {name}")
    ws_manager = ContractWebSocketManager()
    
    try:
        await ws_manager.subscribe_to_events()
        logging.info(f"Subscription complete for {name}")

    except Exception as e:
        logging.error(f"Failed to subscribe to events: {e}")

    except asyncio.TimeoutError:
        logging.error("Time Out!")
        
    except asyncio.CancelledError:
        logging.error("Cancelled!")
    
    return f"Task {name} is complete!"


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
