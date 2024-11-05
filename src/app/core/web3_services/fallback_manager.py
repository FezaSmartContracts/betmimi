import re
import asyncio

from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from websockets import ConnectionClosed, ConnectionClosedError
from redis.asyncio import Redis
import pickle
from app.core.logger import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class FallBackSubscriptionHandler:

    w3_socket: AsyncWeb3 = None

    def __init__(self, wss_url, redis_queue_name: str, subscriptions_queue_name: str):
        self.wss_url = wss_url
        self.redis = Redis(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT, db=0)
        self.redis_queue_name = redis_queue_name
        self.subscriptions_queue_name = subscriptions_queue_name
        self.reconnected = False
    
    async def fetch_logs(self, callback, filter_params) -> None:
        """Connect to the WebSocket and fetch events."""
        try:
            async with AsyncWeb3(WebSocketProvider(self.wss_url)) as self.w3_socket:
                logger.info("Successfully connected to websocket.")
                try:
                    await self._get_logs(callback, filter_params)
                except (ConnectionClosedError, ConnectionClosed) as e:
                    logger.error(f"Disonnected due to {e}. Uninstalled filters")
                except asyncio.CancelledError as e:
                    logger.error(f"Uninstalling filters...{e}")
                except Exception as e:
                    logger.error(f"Unexpected error: {e}.")
        except Exception as e:
            logger.error(f"Disconnected. Uninstalling filters..!")
        

    async def _get_logs(self, callback: callable, filter_params) -> None:
        """Fetches or gets past logs depending on given filter parameters"""
        if self.is_connected():
            lead: str = "Katula"
            fallback_data = {'callback': callback, 'filter_params': filter_params}
            callback_id = f"{lead}{callback}".format()
            await self.redis.set(callback_id, pickle.dumps(fallback_data))

            await asyncio.sleep(2)

            _key = await self.redis.get(callback_id)
            if _key is not None:
                logger.info(f"Key {callback_id} created.")
            else:
                logger.info(f"Key {callback_id} not available")

            logs = await self.w3_socket.eth.get_logs(filter_params)
            try:
                for log in logs:
                    log_dict = {'subscription': callback_id, 'result': log}
                    log_data = pickle.dumps(log_dict)

                    await self.redis.rpush(self.redis_queue_name, log_data)
                    logger.info(f"Added data to queue: {self.redis_queue_name}")
            except (pickle.PickleError, TypeError) as e:
                logger.error(f"Failed to add payload data to queue: {e}")

        else:
            raise RuntimeError("Connection not established, it's not possible to fetch logs")
        
    async def disconnect(self):
        """Gracefully disconnects the WebSocket connection."""
        if self.w3_socket is not None:
            try:
                await self.w3_socket.provider.disconnect()
                self.w3_socket = None
                logger.info("WebSocket connection closed successfully.")
            except Exception as e:
                logger.error(f"Error while closing WebSocket connection: {e}")

    
    def is_connected(self) -> bool:
        """Checks if the WebSocket is connected."""
        return self.w3_socket is not None
    
    async def queue_size(self) -> int:
        """Get the current size of the Redis queue."""
        return await self.redis.llen(self.redis_queue_name)