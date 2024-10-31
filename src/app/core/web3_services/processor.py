from eth_typing import HexStr
import asyncio
from typing import Annotated
from web3 import AsyncWeb3
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
from redis import Redis
import aioredis
import pickle
from ...core.logger import logging
from ...core.db.database import async_get_db

logger = logging.getLogger(__name__)



class BatchProcessor:
    def __init__(self, redis_queue_name: str, redis_inprocess_queue: str, redis_connection: Redis):
        self.redis_queue_name = redis_queue_name
        self.inprocess_queue_name = redis_inprocess_queue
        self.redis = redis_connection
    
    async def batch_process_logs(self, db):
        """
        Fetch a batch of logs from Redis, process them, and store them in the database.

        NOTE: I use BLMOVE which is blocking so as to save resources incase of no acivity.
        """

        while True:
            try:
                log = await self.redis.execute_command('BLMOVE', self.redis_queue_name, self.inprocess_queue_name, 'LEFT', 'RIGHT', 0)
                if log:
                    try:
                        message = pickle.loads(log)
                        
                        sub_id = message["subscription"]
                        if sub_id is None:
                            logger.error("Message missing 'subscription' field.")
                            continue
                        
                        subscription_data_bytes = await self.redis.get(sub_id)
                        if subscription_data_bytes is None:
                            logger.error(f"No subscription data found for sub_id: {sub_id}")
                            continue

                        subscription_data = pickle.loads(subscription_data_bytes)
                        callback_function = subscription_data['callback']
                        if callback_function:
                            logger.info(f"Callback {callback_function} loaded.")
                            await callback_function(message, db)
                            logger.info("Processed log successfully.")
                        else:
                            raise RuntimeError("No callback function returned")
                        await self.redis.lrem(self.inprocess_queue_name, 0, log)
                    except Exception as e:
                        logger.error(f"Failed to process log: {e}")
                else:
                    logger.info("Timeout occurred, no items to move.")
            except ConnectionError as conn_err:
                logger.error(f"Redis connection error: {conn_err}")
            except TimeoutError as timeout_err:
                logger.error(f"Redis timeout error: {timeout_err}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
