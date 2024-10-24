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

    def __init__(self, wss_url):
        self.wss_url = wss_url
        self.redis = Redis(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT, db=0)
    
    async def process_subscriptions(self, ctx) -> None:

        """Connect to the WebSocket and listen for subscription messages."""

        async for self.w3_socket in AsyncWeb3(WebSocketProvider(self.wss_url)):
            try:
                async for message in self.w3_socket.socket.process_subscriptions():
                    sub_id = message["subscription"]
                    callback_data = self.redis.get(sub_id)
                    if callback_data:
                        try:
                            callback = pickle.loads(callback_data)
                            callback(message["result"])
                        except (pickle.PickleError, TypeError) as e:
                            logging.error(f"Failed to deserialize callback for {sub_id}: {e}")
                    else:
                        logging.error(f"Callback for {sub_id} not found")
            except (ConnectionClosedError, ConnectionClosed) as e:
                logging.error(f"Connection interrupted due to {e}. Reconnecting...")
                continue
            except asyncio.CancelledError:
                logging.error("Cancelling subscriptions")
                for sub_id in self.redis.keys():
                    await self.w3_socket.eth.unsubscribe(sub_id)
                break
    
    async def subscribe(self, callback: callable, event_type: SubscriptionType, **event_params) -> HexStr:
        """Subscribes to an event using the existing WebSocket connection."""
        if self.is_connected():
            sub_id = await self.w3_socket.eth.subscribe(event_type, event_params)
            logging.info(f"Subscribed to {sub_id}")
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
    
    def is_connected(self) -> bool:
        """Checks if the WebSocket is connected."""
        return self.w3_socket is not None



class WebSocketManager:
    """
    Manages a WebSocket connection and event subscriptions using a singleton pattern.
    
    Attributes:
        _instance (WebSocketManager): Singleton instance of the class.
        ws_handler (SubscriptionHandler): Handler for managing subscriptions.
        subscription_task (asyncio.Task): Asynchronous task for processing subscriptions.
    """
    
    _instance = None
    
    def __new__(cls, wss_uri):
        """
        Creates a new instance of WebSocketManager if one does not already exist.
        
        Args:
            wss_uri (str): WebSocket URI for establishing the connection.
        
        Returns:
            WebSocketManager: Singleton instance of the class.
        """
        if cls._instance is None:
            cls._instance = super(WebSocketManager, cls).__new__(cls)
            cls._instance.ws_handler = SubscriptionHandler(wss_uri)
            cls._instance.subscription_task = None
        return cls._instance
    
    async def start_processing(self):
        """
        Starts the subscription processing task if it's not already running.
        """
        if not self.subscription_task:
            self.subscription_task = asyncio.create_task(self.ws_handler.process_subscriptions(None))
            logging.info("WebSocket subscription processing started.")
    
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

