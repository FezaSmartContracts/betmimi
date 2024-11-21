from typing import Dict

from app.core.logger import logging
from app.core.constants import MAIL_QUEUE, ALERTS_QUEUE

logger = logging.getLogger(__name__)


events_dict: Dict[str, str] = {
    "general": MAIL_QUEUE,
    "alerts": ALERTS_QUEUE
}

def event_queue_dict() -> Dict[str, str]:
    """Returns a dict of event names and their queue names"""
    try:
       return events_dict
    except Exception as e:
        logger.error(f"Failed to return mail events dict: {e}")