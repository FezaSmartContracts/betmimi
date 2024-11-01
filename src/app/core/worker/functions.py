import asyncio

import uvloop
from arq.worker import Worker
from ...core.config import settings
from ...core.logger import logging
from ..web3_services.processor import BatchProcessor
from ...core.db.database import async_get_db

logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())



# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
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
