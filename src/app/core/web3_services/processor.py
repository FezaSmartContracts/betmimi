from eth_typing import HexStr
import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
from redis import Redis
import aioredis
import pickle
import logging



class BatchProcessor:
    def __init__(self, redis_queue_name: str, redis_inprocess_queue: str, redis_connection: Redis):
        self.redis_queue_name = redis_queue_name
        self.inprocess_queue_name = redis_inprocess_queue
        self.redis = redis_connection
    
    async def batch_process_logs(self):
        """
        Fetch a batch of logs from Redis, process them, and store them in the database.

        NOTE: I use BLMOVE which is blocking so as to save resources incase of no acivity.
        """

        while True:
            try:
                log = await self.redis.execute_command('BLMOVE', self.redis_queue_name, self.inprocess_queue_name, 'LEFT', 'RIGHT', 0)
                if log:
                    try:
                        payload = pickle.loads(log)
                        sub_id = payload["subscription"]
                        callback_function = await self.redis.get(sub_id)
                        if callback_function:
                            callback = pickle.loads(callback_function)
                            callback(payload)
                        logging.info("Processed log successfully.")
                        await self.redis.lrem(self.inprocess_queue_name, 0, log)
                    except Exception as e:
                        logging.error(f"Failed to process log: {e}")
                else:
                    logging.info("Timeout occurred, no items to move.")
            except ConnectionError as conn_err:
                logging.error(f"Redis connection error: {conn_err}")
            except TimeoutError as timeout_err:
                logging.error(f"Redis timeout error: {timeout_err}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
