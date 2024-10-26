import asyncio
import logging
import time

import uvloop
from arq.worker import Worker
from arq import cron
from web3 import AsyncWeb3
from eth_typing import HexStr
from ...core.config import settings
from ...core.utils import queue
from ...models.job import Job
from ..web3_services.manager import WebSocketManager
from ..web3_services.processor import BatchProcessor
from ..web3_services.utils import load_contract_address

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    return f"Task {name} is complete!"

def callback_logs(message):
    logging.info(f"New log received: {message}")


async def subscribe_to_winorloss_arb_usdtv1_events(ctx: Worker, name: str) -> str:
    try:

        WSS_URI = f"wss://arb-sepolia.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"
        _address = load_contract_address("WinOrLoss")
        CONTRACT_ADDRESS = _address

        # Get the singleton instance of the WebSocketManager
        subs_handler = WebSocketManager(WSS_URI, "alchemy_logs_queue")
        await subs_handler.start_processing()

        while not await subs_handler.is_connected():
            logging.info("Not connected")
            await asyncio.sleep(5)
        logging.info("Websocket is sucessfully Connected!")

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
    
async def process_data(ctx: Worker):

    logging.info("Process Data Cron job started")
    redis_connection = ctx['redis']
    bp = BatchProcessor("alchemy_logs_queue", "alchemy_inprocessing_queue", redis_connection)

    try:
        await bp.batch_process_logs()
    except asyncio.CancelledError as e:
        logging.error(f"Cancelled: {e}")
    except Exception as e:
        logging.error(f"Unknown Error: {e}")
    logging.info(f"Task completed its 5-minute run.")

    


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logging.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logging.info("Worker end")
