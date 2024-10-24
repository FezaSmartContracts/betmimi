from typing import Dict
from eth_typing import HexStr
import asyncio
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
import logging

from ...core.utils import queue
from ...models.job import Job

class SubscriptionHandler:
    w3_socket: AsyncWeb3 = None
    callbacks: Dict[HexStr, callable] = {}

    def __init__(self, wss_url):
        self.wss_url = wss_url

    async def process_subscriptions(self) -> None:
        """
        Connect to the WebSocket and listen for subscription messages.
        """

        async for self.w3_socket in AsyncWeb3(WebSocketProvider(self.wss_url)):
            try:
                async for message in self.w3_socket.socket.process_subscriptions():
                    try:
                        self.callbacks[message["subscription"]](message["result"])
                        logging.info(f"Wow! {message}")
                    except ValueError as e:
                        try:
                            logging.error(f"Callback for {message['subscription']} not found")
                        except ValueError as e:
                            logging.error(f"Unexpected response from RPC: {e}")

            except (ConnectionClosedError, ConnectionClosed) as e:
                logging.error(f"Connection interupt due to {e}. Reconnecting...")
                continue
            except asyncio.CancelledError:
                logging.error("Cancelling subscriptions")
                for sub_id in self.callbacks.keys():
                    await self.w3_socket.eth.unsubscribe(sub_id)
                break
        
    async def subscribe(
        self, callback: callable, event_type: SubscriptionType, **event_params
    ) -> HexStr:
        """
        Subscribes to the given event type with the given callback.
        Must be called while process_subscriptions() task is running

        :param callback: The function to call when the event is received
        :param event_type: The event type to subscribe to
        :param event_params: Additional parameters to pass to the subscription
        :return: The subscription ID
        """
        if self.is_connected():
            sub_id = await self.w3_socket.eth.subscribe(event_type, event_params)
            logging.info(f"Subscribed to {sub_id}")
            self.callbacks[sub_id] = callback
            return sub_id
        else:
            raise RuntimeError(
                "Websocket connection not established, it's not possible to subscribe"
            )

    async def unsubscribe(self, sub_id: HexStr) -> None:
        """
        Unsubscribes from a subscription identified by sub_id.
        Must be called while process_subscriptions() task is running

        :param sub_id: The subscription ID to unsubscribe from
        :return: None
        """
        if self.is_connected():
            await self.w3_socket.eth.unsubscribe(sub_id)
            self.callbacks.pop(sub_id)
        else:
            raise RuntimeError(
                "Websocket connection not established, it's not possible to unsubscribe"
            )

    def is_connected(self) -> bool:
        return self.w3_socket is not None



class WebSocketManager:
    _instance = None

    def __new__(cls, wss_uri):
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
            self.subscription_task = asyncio.create_task(self.ws_handler.process_subscriptions())
            logging.info("WebSocket subscription processing started.")

    async def subscribe(self, callback: callable, event_type: str, **event_params):
        """
        Subscribe to an event using the existing connection.
        """
        return await self.ws_handler.subscribe(callback, event_type, **event_params)

    async def is_connected(self) -> bool:
        """
        Check if the WebSocket is connected.
        """
        return self.ws_handler.is_connected()
