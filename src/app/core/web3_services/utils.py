import os
import json
import logging
import asyncio
from typing import Any, Dict
from web3 import AsyncWeb3, WebSocketProvider
from eth_abi import decode

from ...core.utils import queue
from ...models.job import Job


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

# -------- Utility Functions ---------
def load_abi(file_path: str) -> Dict[str, Any]:
    """Load contract ABI from a JSON file."""
    with open(file_path, "r") as file:
        return json.load(file)

def load_contract_address(key: str) -> str:
    """Fetch contract address by key."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../artifacts/deployments.json')
    with open(file_path, 'r') as file:
        contracts = json.load(file)
    if key in contracts:
        return contracts[key]['contract_address']
    logger.error(f"Contract with key: {key} not found")
    raise ValueError(f"Contract with key: {key} not found.")


#------------------------subscription functions----------------------#
async def subscribe_to_usdtv1_events(w3):
    CONTRACT_ADDRESS = load_contract_address("WinOrLoss")
    deposited_event_topic = w3.keccak(text="Deposited(address)")

    filter_params = {
        "address": CONTRACT_ADDRESS,
        "topics": [deposited_event_topic]
    }

    try:
        subscription_id = await w3.eth.subscribe("logs", filter_params)
        logging.info(f"Subscribed to Deposited events with subscription ID: {subscription_id}")

        async for payload in w3.socket.process_subscriptions():
            logging.info(f"Received subscription payload: {payload}")
            result = payload.get("result")
            if not result:
                logging.error(f"No result found in payload: {payload}")
                continue

            from_addr = decode(["address"], result["topics"][1])[0]
            logging.info(f"Deposited Event from: {from_addr}")

    except TimeoutError:
        logging.error("Subscription process timed out. Retrying...")

    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

async def reschedule_jobs():
    message = "New Job"
    job = await queue.pool.enqueue_job("subscribe_to_events", message, _defer_by=60)
    logging.info(f"Created new job id: {job.job_id}")
