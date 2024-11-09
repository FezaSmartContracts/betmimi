import re
import asyncio
from typing import List

from eth_typing import HexStr
from web3 import AsyncWeb3
from web3.providers.persistent import WebSocketProvider
from web3.types import SubscriptionType
from websockets import ConnectionClosed, ConnectionClosedError
from redis.asyncio import Redis
import pickle
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from app.core.logger import logging
from app.core.config import settings
from .topics import event_queue_dict

logger = logging.getLogger(__name__)

class MailboxManager:

    def __init__(self):
        self.redis = Redis(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT, db=0)

    async def add_address_to_list(self, address: str, relevant_queue_name: str) -> None:
        try:
            await self.redis.rpush(relevant_queue_name, address)
            logger.info(f"Email {address} added to Queue")
        except Exception as e:
            logger.error(f"Failed to add email to queue due to: {e}")
    
    async def process_emails(self) -> None:
        try:
            event_queues = event_queue_dict()
            for key, value in event_queues.items():
                email_addresses = await self.redis.lrange(value, 0, -1)
                await self.redis.ltrim(value, 1, 0)  
                email_addresses = [email.decode('utf-8') if isinstance(email, bytes) else str(email) for email in email_addresses]
                await self._process_emails(email_addresses)
        except Exception as e:
            logger.error(f"Failed to process emails: {e}")

    async def _process_emails(self, emails: List[str]):
        to_emails = [To(email) for email in emails]
        message = Mail(
        from_email=settings.FROM_EMAIL,
        to_emails=to_emails,
        subject="Julie!",
        html_content="GoodMorning"
        )

        try:
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info(f"Email sent successfully to {emails}. Status code: {response.status_code}")
    
        except Exception as e:
            logger.error(f"Failed to process email: {e}")
    
    