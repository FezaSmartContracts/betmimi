import logging
import json
from hexbytes import HexBytes
from .handlers import (
    usdtv1_event_topics_dict,
    usdtv1_event_handlers
)

async def process_winorloss_callbacklogs(message):
    """Callback function for updating/persisting data to database."""
    try:
        payload = message['result']
        event_topics = usdtv1_event_topics_dict()
        event_handlers = usdtv1_event_handlers()
        event_signature: HexBytes = payload['topics'][0]

        if not event_topics:
            logging.error("No event topics loaded; aborting log processing.")
            return

        for event, topic in event_topics.items():
            if event_signature == topic:
                if handler := event_handlers.get(event):
                    await handler(payload)
                    logging.info(f"Event '{event}' processed.")
                    break
                else:
                    logging.warning(f"No handler defined for event '{event}'.")
                    break
        else:
            logging.error("Event log cannot be identified!")

    except FileNotFoundError:
        logging.error("ABI file not found.")
    except json.JSONDecodeError:
        logging.error("Invalid JSON format in ABI file.")
    except Exception as e:
        logging.error(f"Error processing event log: {e}")
