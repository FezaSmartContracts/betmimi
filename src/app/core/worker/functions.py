import asyncio
from typing import Annotated

import uvloop
from arq.worker import Worker
from eth_typing import HexStr
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...core.config import settings
from ...core.utils import queue
from ...models.job import Job
from ...core.logger import logging
from ..web3_services.manager import WebSocketManager
from ..web3_services.processor import BatchProcessor
from ...core.db.database import async_get_db
from ..web3_services.utils import arbitrum_contract_addresses
from ..web3_services.arbitrum_one.callbacks import process_arbitrum_callbacklogs

logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())



# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    return f"Task {name} is complete!"

def callback_logs(message):
    logger.info(f"New log received: {message}")


async def subscribe_to_winorloss_arb_usdtv1_events(ctx: Worker, name: str) -> str:
    try:

        WSS_URI = f"wss://arb-sepolia.g.alchemy.com/v2/{settings.ALCHEMY_API_KEY}"
        CONTRACT_ADDRESSES = arbitrum_contract_addresses()

        # Get the singleton instance of the WebSocketManager
        subs_handler = WebSocketManager(WSS_URI, "alchemy_logs_queue")
        await subs_handler.start_processing()

        while not await subs_handler.is_connected():
            logger.info("Not connected")
            await asyncio.sleep(5)
        logger.info("Websocket is sucessfully Connected!")

        await subs_handler.subscribe(
            process_arbitrum_callbacklogs, "logs", address=CONTRACT_ADDRESSES
        )
    except Exception as e:
        logger.error(f"Failed to subscribe to events: {e}")
    except asyncio.TimeoutError:
        logger.error("Time Out!")
    except asyncio.CancelledError:
        logger.error("Cancelled!")
        return f"Task {name} is complete!"
    
async def process_data(ctx: Worker):

    logger.info("Process Data Cron job started")
    redis_connection = ctx['redis']

    async for db in async_get_db():
        bp = BatchProcessor("alchemy_logs_queue", "alchemy_inprocessing_queue", redis_connection)

        try:
            await bp.batch_process_logs(db)
        except asyncio.CancelledError as e:
            logger.error(f"Cancelled: {e}")
        except Exception as e:
            logger.error(f"Unknown Error: {e}")
        logger.info(f"Task completed its 5-minute run.")

    


# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logger.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logger.info("Worker end")
