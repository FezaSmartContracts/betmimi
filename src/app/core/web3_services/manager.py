from eth_typing import HexStr
import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
from redis import Redis
import pickle
import logging

from ..config import settings

class SubscriptionHandler:

    w3_socket: AsyncWeb3 = None

    def __init__(self, wss_url, redis_queue_name: str):
        self.wss_url = wss_url
        self.redis = Redis(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT, db=0)
        self.redis_queue_name = redis_queue_name
    
    async def process_subscriptions(self, ctx) -> None:

        """Connect to the WebSocket and listen for subscription messages."""

        async for self.w3_socket in AsyncWeb3(WebSocketProvider(self.wss_url)):
            try:
                async for payload in self.w3_socket.socket.process_subscriptions():

                    log_data = pickle.dumps(payload)
                    try:
                        self.redis.rpush(self.redis_queue_name, log_data)
                        logging.info(f"Added data to queue: {self.redis_queue_name}")
                    except (pickle.PickleError, TypeError) as e:
                        logging.error(f"Failed to add payload data to queue: {e}")
    
            except (ConnectionClosedError, ConnectionClosed) as e:
                logging.error(f"Connection interrupted due to {e}. Reconnecting...")
                continue
            except asyncio.CancelledError:
                logging.error("Cancelling subscription processing. Cleaning up....")
                await self._cleanup_subscriptions()
                break
            except Exception as e:
                logging.error(f"Unexpected error: {e}. Reconnecting...")
                continue
    
    async def subscribe(self, callback: callable, event_type: SubscriptionType, **event_params) -> HexStr:
        """Subscribes to an event using the existing WebSocket connection."""
        if self.is_connected():
            sub_id = await self.w3_socket.eth.subscribe(event_type, event_params)
            logging.info(f"Subscribed to {event_type} with subscription ID {sub_id}")
            self.redis.set(sub_id, pickle.dumps(callback))
            return sub_id
        else:
            raise RuntimeError("WebSocket connection not established, it's not possible to subscribe")
    
    async def unsubscribe(self, sub_id: HexStr) -> None:
        """Unsubscribes from a subscription identified by sub_id."""
        if self.is_connected():
            await self.w3_socket.eth.unsubscribe(sub_id)
            self.redis.delete(sub_id)
        else:
            raise RuntimeError("WebSocket connection not established, it's not possible to unsubscribe")
        
    async def _cleanup_subscriptions(self) -> None:
        """Unsubscribe from all active subscriptions"""
        for sub_id in self.redis.keys():
            try:
                await self.w3_socket.eth.unsubscribe(sub_id)
                logging.info(f"Unsubscribed from {sub_id}")
            except Exception as e:
                logging.error(f"Failed to unsubscribe from {sub_id}: {e}")
    
    def is_connected(self) -> bool:
        """Checks if the WebSocket is connected."""
        return self.w3_socket is not None
    
    def queue_size(self) -> int:
        """Get the current size of the Redis queue."""
        return self.redis.llen(self.redis_queue_name)



class WebSocketManager:
    """
    Manages a WebSocket connection and event subscriptions using a singleton pattern.
    
    Attributes:
        _instance (WebSocketManager): Singleton instance of the class.
        ws_handler (SubscriptionHandler): Handler for managing subscriptions.
        subscription_task (asyncio.Task): Asynchronous task for processing subscriptions.
    """
    
    _instance = None
    
    def __new__(cls, wss_uri, redis_queue_name: str):
        """
        Creates a new instance of WebSocketManager if one does not already exist.
        
        Args:
            wss_uri (str): WebSocket URI for establishing the connection.
            redis_queue_name (str): Name of queue
        
        Returns:
            WebSocketManager: Singleton instance of the class.
        """
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.ws_handler = SubscriptionHandler(wss_uri, redis_queue_name)
            cls._instance.subscription_task = None
        return cls._instance
    
    async def start_processing(self):
        """
        Starts the subscription processing task if it's not already running.
        """
        if not self.subscription_task:
            self.subscription_task = asyncio.create_task(self.ws_handler.process_subscriptions(None))
            logging.info("Initial Websocket Connection Starting.")
    
    async def subscribe(self, callback: callable, event_type: str, **event_params):
        """
        Subscribes to an event using the existing WebSocket connection.
        
        Args:
            callback (callable): Function to call when the event is received.
            event_type (str): Type of event to subscribe to.
            event_params (dict): Additional parameters for the event subscription.
        
        Returns:
            The result of the subscription request.
        """
        return await self.ws_handler.subscribe(callback, event_type, **event_params)
    
    async def is_connected(self) -> bool:
        """
        Checks if the WebSocket is connected.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        return self.ws_handler.is_connected()
    
    async def get_queue_size(self) -> int:
        """
        Returns the cureent queue size.

        Returns:
            int: Integer value. Zero if empty
        """
        return self.ws_handler.queue_size()