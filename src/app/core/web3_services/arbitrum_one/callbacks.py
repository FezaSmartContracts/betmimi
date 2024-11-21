import json
from hexbytes import HexBytes

from app.core.logger import logging
from app.core.web3_services.arbitrum_one.event_topics import usdtv1_event_topics_dict
from app.core.web3_services.arbitrum_one.handler import usdtv1_event_handlers


logger = logging.getLogger(__name__)

async def process_arbitrum_callbacklogs(message, db):
    """Callback function for updating/persisting data to database."""
    try:
        payload = message['result']
        event_topics = usdtv1_event_topics_dict()
        event_handlers = usdtv1_event_handlers()
        event_signature: HexBytes = payload['topics'][0]

        if not event_topics:
            logger.error("No event topics loaded; aborting log processing.")
            return

        for event, topic in event_topics.items():
            if event_signature == topic:
                if handler := event_handlers.get(event):
                    await handler(
                        payload, db
                    )
                    logger.info(f"Event '{event}' processed.")
                    break
                else:
                    logger.warning(f"No handler defined for event '{event}'.")
                    break
        else:
            logger.error("Event log cannot be identified!")

    except FileNotFoundError:
        logger.error("ABI file not found.")
    except json.JSONDecodeError:
        logger.error("Invalid JSON format in ABI file.")
    except Exception as e:
        logger.error(f"Error processing event log: {e}")
