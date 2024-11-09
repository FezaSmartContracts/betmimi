import asyncio

import uvloop
from redis.asyncio import Redis
from arq.worker import Worker
from ...core.logger import logging
from ..web3_services.processor import BatchProcessor
from ..akabokisi.manager import MailboxManager
from ..constants import ALCHEMY_REDIS_QUEUE_NAME, ALCHEMY_INPROCESSING_QUEUE
from ...core.db.database import async_get_db
from ..web3_services.arbitrum_one.functions import queue_missed_events_for_usdtv1_arb_alchemy
from app.core.config import settings

logger = logging.getLogger(__name__)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())



# -------- background tasks --------
async def sample_background_task(ctx: Worker, name: str) -> str:
    await asyncio.sleep(5)
    return f"Task {name} is complete!"

async def send_email(ctx: Worker, name: str) -> str:
    mail = MailboxManager()
    try:
        await mail.process_emails()
        logger.info(f"Emails Sent!")
    except Exception as e:
        logger.error(f"Email sending failed due to: {e}")
    return f"Task {name} is complete!"
    
async def process_data(ctx):
    logger.info("Process Data Cron job started")
    redis_connection: Redis = ctx['redis']

    async for db in async_get_db():
        bp = BatchProcessor(
            ALCHEMY_REDIS_QUEUE_NAME,
            ALCHEMY_INPROCESSING_QUEUE,
            redis_connection
        )

        try:
            await bp.batch_process_logs(db)
        except asyncio.CancelledError as e:
            logger.error(f"Cancelled: {e}")
        except Exception as e:
            logger.error(f"Unknown Error: {e}")
        logger.info(f"Task completed its 10-minute(s) run.")

async def call_usdtv1_arb_alchemy_fallback(
        ctx: Worker,
        name: str,
        from_block: int,
        to_block: int
    ) -> None:
    timeout = 2 * settings.WEBSOCKET_TIMEOUT
    try:
        await asyncio.wait_for(
            queue_missed_events_for_usdtv1_arb_alchemy(from_block, to_block),
            timeout=float(timeout)
        )
    except asyncio.TimeoutError:
        logger.error("Time Out")
    except asyncio.CancelledError as e:
        logger.error(f"Cancelled: {e}")
        raise
    except Exception as e:
        logger.error(f"Unknown Error: {e}")
    logger.info(f"Task `{name}` completed its run.")
    
# -------- base functions --------
async def startup(ctx: Worker) -> None:
    logger.info("Worker Started")


async def shutdown(ctx: Worker) -> None:
    logger.info("Worker end")
