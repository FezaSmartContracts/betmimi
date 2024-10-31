import os
import json
from typing import Any, Dict, List
from hexbytes import HexBytes
from eth_utils import keccak

from ...core.logger import logging

logger = logging.getLogger(__name__)

def load_abi(relative_path: str) -> Dict[str, Any]:
    """Load contract ABI from a JSON file located relative to the calling file.
    
    In the calling file, Pass the relative path to the ABI file based on the module's location

    Forexample: abi = `load_abi("../artifacts/arbitrum/MyContract.json")`
    >>>
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, relative_path)
    
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logger.error(f"ABI file not found at: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from file: {file_path}")
        raise

def load_contract_address(key: str, relative_path: str) -> str:
    """
    Fetch contract address by key.

    In the calling file, Pass the relative path to the ABI file based on the module's location

    Forexample: abi = `load_abi("../artifacts/arbitrum/deployments.json")`
    >>>
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, relative_path)
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

def arbitrum_contract_addresses():
    address_relative_path = "../artifacts/arbitrum/deployments.json"
    _keys = ["WinOrLoss", "ZUSDTv1" "OUSDTv1", "TUSDTv1", "HUSDTv1"]
    arbitrum_address = []

    for _key in _keys:
        _address = load_contract_address(_key, address_relative_path)
        arbitrum_address.append(_address)
        return arbitrum_address
