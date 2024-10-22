import websockets
import logging
import asyncio
from web3 import AsyncWeb3, WebSocketProvider
from asyncio import TimeoutError, sleep
logging.basicConfig(level=logging.INFO)

from ..worker.settings import settings
from .utils import subscribe_to_usdtv1_events, reschedule_jobs

logger = logging.getLogger(__name__)

RETRY_DELAY = 5


class ContractWebSocketManager:
    """Handles WebSocket connection and event listening for different contracts."""
    
    def __init__(self):
        self.API_KEY = settings.ALCHEMY_API_KEY
        self.PROVIDER_URI = f"wss://arb-sepolia.g.alchemy.com/v2/{self.API_KEY}"

     
    async def subscribe_to_events(self):
        """
        Method for subscribing to events. 
        
        Please note in an attempt to create an indefinite websocket connection, 
        I use a `for` loop instead of a `while` loop. A lot of controversies;
        1. https://stackoverflow.com/questions/56161595/how-to-use-async-for-in-python
        2. https://web3py.readthedocs.io/en/stable/providers.html#using-persistent-connection-providers
        """

        logging.info("Connecting to WebSocket...")
        async for w3 in AsyncWeb3(WebSocketProvider(self.PROVIDER_URI)):
            try:
                logging.info(f"Successfully connected to: {self.PROVIDER_URI}")

                await subscribe_to_usdtv1_events(w3)
                # ----more subscriptions here

            except websockets.ConnectionClosed as e:
                logging.error(f"WebSocket connection closed: {e}. Reconnecting in {RETRY_DELAY} seconds...")
                await sleep(RETRY_DELAY)
                continue

            except asyncio.TimeoutError as e:
                logging.error(f"WebSocket connection timeout: {e}. Reconnecting in {RETRY_DELAY} seconds...")
                await sleep(RETRY_DELAY)

            except Exception as e:
                logging.error(f"Unexpected error: {e}. Reconnecting in {RETRY_DELAY} seconds...")
                await sleep(RETRY_DELAY)


    async def unsubscribe_from_all_events(self):
        if None:
            pass

        async with AsyncWeb3(WebSocketProvider(self.PROVIDER_URI)) as w3:
            pass