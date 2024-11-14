from web3 import Web3
from ..manager import Web3HttpConnectionManager
from ....logger import logging
from ...utils import load_abi, load_contract_address, arbitrum_contract_addresses_and_names, return_abi_paths

logger = logging.getLogger(__name__)

contracts_relative_path = "../artifacts/arbitrum/deployments.json"

async def get_count_for_usdt_contracts(match_id: int) -> dict:
    """Reads count for predictions from all contracts """
    _list = arbitrum_contract_addresses_and_names()
    function_name = "counter"
    args = (match_id,)
    data_dict = {"data": []}

    try:
        manager = Web3HttpConnectionManager()
        for _tuple in _list:
            abi_path = f"../artifacts/arbitrum/{_tuple[0]}.json"
            address = _tuple[1]
            name = _tuple[0]
            abi = load_abi(abi_path)
            
            data = await manager.fetch_contract_data(address, abi, function_name, *args)
            data_dict["data"].append((name, data))
            
        return data_dict
    except Exception as e:
        logger.error(f"Unknown Error Occurred: {e}")
        return {"data": []}

async def is_admin(address: str, _key: str) -> bool:
    """
    Checks if a given address(`address`) is an admin to a given contract(Identified by `_key` e.g `WinOrLoss`)
    """
    contract_address = load_contract_address(_key, contracts_relative_path)
    address = Web3.to_checksum_address(address)
    for key, value in return_abi_paths().items():
        if _key == key:
            abi = load_abi(value)
    function_name = f"admin"
    args = (address,)

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(contract_address, abi, function_name, *args)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")

async def is_whitelisted(address: str, _key: str) -> bool:
    """
    Checks if a given address(`address`) is whitelisted by a given contract(Identified by `_key` e.g `Usdt`)
    """
    contract_address = load_contract_address(_key, contracts_relative_path)
    address = Web3.to_checksum_address(address)
    for key, value in return_abi_paths().items():
        if _key == key:
            abi = load_abi(value)
    function_name = f"whitelisted"
    args = (address,)

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(contract_address, abi, function_name, *args)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")

async def current_owner(_key: str) -> str:
    """
    Returns the owner of a given contract(`_key`)
    """
    contract_address = load_contract_address(_key, contracts_relative_path)
    for key, value in return_abi_paths().items():
        if _key == key:
            abi = load_abi(value)
    function_name = f"owner"

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(contract_address, abi, function_name)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")

async def future_owner(_key: str) -> str:
    """
    Returns the future/pending owner of a given contract(`_key`)
    """
    contract_address = load_contract_address(_key, contracts_relative_path)
    for key, value in return_abi_paths().items():
        if _key == key:
            abi = load_abi(value)
    function_name = f"pending_owner"

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(contract_address, abi, function_name)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")

async def fee_percentage(_key: str) -> str:
    """
    Returns the current fee percentage for a given contract
    """
    contract_address = load_contract_address(_key, contracts_relative_path)
    for key, value in return_abi_paths().items():
        if _key == key:
            abi = load_abi(value)
    function_name = f"fee_percent"

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(contract_address, abi, function_name)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")

async def game_info(match_id: int, _key: str = "Games"):
    """
    Returns information about a given on-chain registered game.
    """
    contract_address = load_contract_address(_key, contracts_relative_path)
    for key, value in return_abi_paths().items():
        if _key == key:
            abi = load_abi(value)
    function_name = f"games"
    args = (match_id,)

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(contract_address, abi, function_name, *args)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")