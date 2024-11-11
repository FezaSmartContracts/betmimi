import os
import pickle
from typing import List, Dict
from jinja2 import Environment, FileSystemLoader, select_autoescape
from redis.asyncio import Redis
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To
from app.core.logger import logging
from app.core.config import settings
from .topics import event_queue_dict
from ..constants import USER_NAME
from .messages import support_link
from .helper import current_year

logger = logging.getLogger(__name__)

template_dir = os.path.join(os.path.dirname(__file__), "templates")

env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(["html", "xml"])
)

class MailboxManager:
    def __init__(self):
        self.redis = Redis(host=settings.REDIS_QUEUE_HOST, port=settings.REDIS_QUEUE_PORT, db=0)

    async def add_data_to_list(self, addresses: List[str], relevant_queue_name: str, subject: str, body: str) -> None:
        """Adds email data for multiple addresses to Redis queue."""
        try:
            for address in addresses:
                _data = {"address": address, "subject": subject, "body": body}
                data = pickle.dumps(_data)
                await self.redis.rpush(relevant_queue_name, data)
                logger.info(f"Email {address} added to Queue")
        except Exception as e:
            logger.error(f"Failed to add emails to queue due to: {e}")
    
    async def process_emails(self) -> None:
        try:
            event_queues = event_queue_dict()
            for queue_name in event_queues.values():
                data = await self.redis.lrange(queue_name, 0, -1)
                await self.redis.ltrim(queue_name, 1, 0)  # Clear the queue after fetching

                # Batch emails by subject and body
                batch = self._group_emails_by_content(data)

                # Send emails in batches
                for (subject, body), email_addresses in batch.items():
                    await self._process_emails(email_addresses, subject, body)
        except Exception as e:
            logger.error(f"Failed to process emails: {e}")

    def _group_emails_by_content(self, data: List[bytes]) -> Dict[tuple, List[str]]:
        """
        Groups emails by subject and body for batch processing.
        Returns a dictionary where each key is a (subject, body) tuple,
        and each value is a list of email addresses.
        """
        batch = {}
        for _data in data:
            email_data = pickle.loads(_data)
            subject = email_data["subject"]
            body = email_data["body"]
            address = email_data["address"]

            key = (subject, body)
            if key not in batch:
                batch[key] = []
            batch[key].append(address)
        
        return batch

    async def _process_emails(self, emails: List[str], subject: str, body: str):
        """Send batch emails using SendGrid"""
        try:
            template = env.get_template("email_template.html")
            html_content = template.render(
                body_message=body,
                recipient_name=USER_NAME,
                support_link=support_link(),
                current_year=current_year()
            )

            to_emails = [To(email) for email in emails]
            message = Mail(
                from_email=settings.FROM_EMAIL,
                to_emails=to_emails,
                subject=subject,
                html_content=html_content
            )

            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info(f"Batch email sent successfully to {len(emails)} recipients. Status code: {response.status_code}")

        except Exception as e:
            logger.error(f"Failed to send batch email to {emails}: {e}")
