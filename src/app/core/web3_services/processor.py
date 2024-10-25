from eth_typing import HexStr
import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
from redis import Redis
import pickle
import logging



class BatchProcessor:
    def __init__(self, redis_queue_name: str, redis_connection: Redis):
        self.redis_queue_name = redis_queue_name
        self.redis = redis_connection
    
    async def batch_process_logs(self):
        """
        Fetch a batch of logs from Redis, process them, and store them in the database.
        """
        logs_to_process = []
        batch_size = await self.redis.llen(self.redis_queue_name)
        
        for _ in range(batch_size):
            log = await self.redis.lpop(self.redis_queue_name)
            if log:
                logs_to_process.append(pickle.loads(log))
            else:
                break
        
        if logs_to_process:
            for payload in logs_to_process:
                sub_id = payload["subscription"]
                callback_function = await self.redis.get(sub_id)
                if callback_function:
                    callback = pickle.loads(callback_function)
                    callback(payload)
            logging.info(f"Processed batch of {len(logs_to_process)} logs.")
        else:
            logging.info("List 'logs_to_process' is empty")
