import asyncio
import logging

import uvloop
from arq.worker import Worker
from web3 import AsyncWeb3
from eth_typing import HexStr
from ..web3_services.manager import SubscriptionHandler
from ...core.config import settings
from ...core.utils import queue
from ...models.job import Job
from ..web3_services.manager import WebSocketManager
#from ..web3_services.utils import subscribe_to_usdtv1_events

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    return f"Task {name} is complete!"

def callback_logs(message):
    logging.info(f"New log received: {message}")


async def process_event(ctx: Worker, name: str) -> str:
    try:

        WSS_URI = f"wss://arb-sepolia.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"
        deposited_event_topic = AsyncWeb3.keccak(text="Deposited(address)")
        CONTRACT_ADDRESS = "0xD17db0380C27aD1417B02f923648c136EF807D3c"

        filter_params = {
            "address": CONTRACT_ADDRESS,
            "topics": [deposited_event_topic]
        }
        # Get the singleton instance of the WebSocketManager
        subs_handler = WebSocketManager(WSS_URI)

        await subs_handler.start_processing()

        while not await subs_handler.is_connected():
            logging.info("Not connected")
            await asyncio.sleep(1)
        logging.info("Congs, Connected!")

        # Subscribes to desired events
        await subs_handler.subscribe(
            callback_logs, "logs", address=CONTRACT_ADDRESS
        )
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
