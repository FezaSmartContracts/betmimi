import re
import asyncio

from eth_typing import HexStr
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
from redis.asyncio import Redis
import pickle
from app.core.logger import logging
from app.core.config import settings
from app.core.akabokisi.manager import MailboxManager
from app.core.db.database import async_get_db
from app.core.akabokisi.messages import on_websocket_disconnect, on_websocket_reconnect
from app.core.web3_services.arbitrum_one.handlers.helper import get_admin_emails
from app.schemas.users import QuickAdminRead
from app.core.constants import websocket_disconnected, websocket_reconnected

logger = logging.getLogger(__name__)

class SubscriptionHandler:

    w3_socket: AsyncWeb3 = None

    def __init__(self, wss_url, redis_queue_name: str, subscriptions_queue_name: str):
        self.wss_url = wss_url
        self.redis = Redis(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT, db=0)
        self.redis_queue_name = redis_queue_name
        self.subscriptions_queue_name = subscriptions_queue_name
        self.reconnected = False
    
    async def process_subscriptions(self) -> None:
        """Connect to the WebSocket and listen for subscription messages."""
        try:
            async for self.w3_socket in AsyncWeb3(WebSocketProvider(self.wss_url)):
                # Check if reconnection has occurred
                if self.reconnected:
                    await self._resubscribe()
                    await self.monitor_reconnection()
                self.reconnected = False

                try:
                    async for payload in self.w3_socket.socket.process_subscriptions():
                        log_data = pickle.dumps(payload)
                        try:
                            await self.redis.rpush(self.redis_queue_name, log_data)
                            logger.info(f"Added data to queue: {self.redis_queue_name}")
                        except (pickle.PickleError, TypeError) as e:
                            logger.error(f"Failed to add payload data to queue: {e}")

                except (ConnectionClosedError, ConnectionClosed) as e:
                    logger.error(f"Connection interrupted due to {e}. Reconnecting...")
                    self.reconnected = True
                    await self.monitor_disconnection()
                    continue
                except asyncio.CancelledError as e:
                    logger.error(f"Cancelling subscription processing. Cleaning up....: {e}")
                    await self._cleanup_subscriptions()
                    break
                except Exception as e:
                    logger.error(f"Unexpected error: {e}. Reconnecting...")
                    self.reconnected = True
                    await self.monitor_disconnection()
                    continue
        except Exception as e:
            logger.error(f"Max retries 5 reached. Exited loop!")

    
    async def subscribe(self, callback: callable, event_type: SubscriptionType, **event_params) -> HexStr:
        """Subscribes to an event using the existing WebSocket connection."""
        if self.is_connected():
            sub_id = await self.w3_socket.eth.subscribe(event_type, event_params)
            logger.info(f"Subscribed to {event_type} with subscription ID {sub_id}")

            subscription_data = {'callback': callback, 'event_type': event_type, 'event_params': event_params}
            await self.redis.set(sub_id, pickle.dumps(subscription_data))

            await self.redis.rpush(self.subscriptions_queue_name, sub_id) # store subscription id in queue

            return sub_id
        else:
            raise RuntimeError("WebSocket connection not established, it's not possible to subscribe")
    
    async def unsubscribe(self, sub_id: HexStr) -> bool:
        """Unsubscribes from a subscription identified by sub_id."""
        if self.is_connected():
            unsubscribed = await self.w3_socket.eth.unsubscribe(sub_id)
            await self.redis.delete(sub_id)
            if unsubscribed:
                return True
            else:
                return False
        else:
            raise RuntimeError("WebSocket connection not established, it's not possible to unsubscribe")
        
    async def _cleanup_subscriptions(self) -> None:
        """Unsubscribe from all active subscriptions retrieved from the Redis queue."""
        while True:
            sub_id = await self.redis.lpop(self.subscriptions_queue_name)

            if sub_id is None:
                break

            try:
                sub_id_str = sub_id.decode('utf-8')
                unsubscribed = await self.unsubscribe(sub_id_str)
                if unsubscribed:
                    logger.info(f"Successfully Unsubscribed from {sub_id_str}")
                else:
                    logger.info(f"Failed to Unsubscribe from {sub_id_str}")
            except Exception as e:
                logger.error(f"Failed to unsubscribe from {sub_id_str}: {e}")


    async def _resubscribe(self) -> None:
        """Resubscribe to events on reconnect."""
        while await self.redis.llen("subscriptions_queue") > 0:
            try:
                # Pop the first sub_id from the subscriptions_queue
                sub_id = await self.redis.lpop(self.subscriptions_queue_name)
                if sub_id is None:
                    logger.warning("No more subscriptions to resubscribe.")
                    break

                # Decode the sub_id from bytes to a string
                sub_id_str = sub_id.decode("utf-8")

                # Retrieve the subscription data from Redis
                subscription_data_bytes = await self.redis.get(sub_id_str)
                if subscription_data_bytes is None:
                    logger.warning(f"No subscription data found for ID {sub_id_str}")
                    continue

                # Deserialize the subscription data
                subscription_data = pickle.loads(subscription_data_bytes)
                callback = subscription_data['callback']
                event_type = str(subscription_data['event_type'])
                event_params = list(subscription_data['event_params']['address'])

                # Resubscribe with the original data
                await self.subscribe(callback, event_type, address=event_params)
                logger.info(f"Successfully resubscribed to {event_type} previously held by subscription ID: {sub_id_str}")

                break # ensures we only retrieve the first element of the list

            except Exception as e:
                logger.error(f"Failed to resubscribe to subscription ID {sub_id}: {e}")

    async def monitor_disconnection(self):
        try:
            async for db in async_get_db():
                mail = MailboxManager()
                subject, queue_name = websocket_disconnected()
                message = on_websocket_disconnect()
                    
                addresses = await get_admin_emails(db, QuickAdminRead)
                await mail.add_data_to_list(
                    addresses,
                    queue_name,
                    subject,
                    message
                )
                break
        except Exception as e:
            logger.error(f"Error while monitoring: {e}")

    async def monitor_reconnection(self):
        try:
            async for db in async_get_db():
                mail = MailboxManager()
                subject, queue_name = websocket_reconnected()
                message = on_websocket_reconnect()
                    
                addresses = await get_admin_emails(db, QuickAdminRead)
                await mail.add_data_to_list(
                    addresses,
                    queue_name,
                    subject,
                    message
                )
                break
        except Exception as e:
            logger.error(f"Error while monitoring reconnects: {e}")

    
    def is_connected(self) -> bool:
        """Checks if the WebSocket is connected."""
        return self.w3_socket is not None
    
    async def queue_size(self) -> int:
        """Get the current size of the Redis queue."""
        return await self.redis.llen(self.redis_queue_name)