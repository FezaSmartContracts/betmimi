from typing import Dict, List

from ..logger import logging
from ..constants import GAME_REGISTERED

logger = logging.getLogger(__name__)


events_dict: Dict[str, str] = {
    "game_registered_event": GAME_REGISTERED
}

def event_queue_dict() -> Dict[str, str]:
    """Returns a dict of event names and their queue names"""
    try:
       return events_dict
    except Exception as e:
        logger.error(f"Failed to return mail events dict: {e}")