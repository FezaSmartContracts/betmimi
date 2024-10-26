import os
import json
import logging
from typing import Any, Dict, List
from hexbytes import HexBytes
from eth_utils import keccak

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_abi(file_path: str) -> Dict[str, Any]:
    """Load contract ABI from a JSON file."""
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"ABI file not found at: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from file: {file_path}")
        raise

def load_contract_address(key: str) -> str:
    """Fetch contract address by key."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, '../artifacts/deployments.json')
    try:
        with open(file_path, 'r') as file:
            contracts = json.load(file)
    except FileNotFoundError:
        logger.error(f"Contracts file not found at: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from contracts file: {file_path}")
        raise

    if key in contracts:
        return contracts[key]['contract_address']
    logger.error(f"Contract with key '{key}' not found in contracts file.")
    raise ValueError(f"Contract with key '{key}' not found.")

def get_event_topic(abi: List[Dict[str, Any]], event_name: str) -> HexBytes:
    """
    Fetch contract events and return a built event signature string.
    """
    for item in abi:
        if item.get("type") == "event" and item.get("name") == event_name:
            types = ",".join(input["type"] for input in item["inputs"])
            event_signature = f"{event_name}({types})"
            return keccak(text=event_signature)
    logger.error(f"Event '{event_name}' not found in ABI.")
    raise ValueError(f"Event '{event_name}' not found in ABI.")
