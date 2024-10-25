import os
import json
import logging
import asyncio
from typing import Any, Dict
from web3 import AsyncWeb3, WebSocketProvider
from eth_abi import decode

from ...utils import queue
from ....models.job import Job
from ..manager import SubscriptionHandler


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


sub_mappings: Dict[int, int]
sub_mappings = {1: "", 2: ""}

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
async def subscribe_to_usdtv1_events(message, w3: AsyncWeb3):
    logging.info(f"New log received: {message}")
    CONTRACT_ADDRESS = load_contract_address("WinOrLoss")
    deposited_event_topic = w3.keccak(text="Deposited(address)")

    filter_params = {
        "address": CONTRACT_ADDRESS,
        "topics": [deposited_event_topic]
    }


