
from ..manager import Web3HttpConnectionManager
from ....logger import logging
from ...utils import load_abi, load_contract_address, arbitrum_contract_addresses_and_names

logger = logging.getLogger(__name__)

contracts_relative_path = "../artifacts/arbitrum/deployments.json"
USDTV1_ABI_PATH = "../artifacts/arbitrum/USDTv1.json"
BALANCE_USDT_ABI_PATH = "../artifacts/arbitrum/UsdtManager.json"
GAMES_MANAGER = "../artifacts/arbitrum/GamesManager.json"

async def get_count_for_usdtv1(match_id: int) -> int:
    address = load_contract_address("WinOrLoss", contracts_relative_path)
    abi = load_abi(USDTV1_ABI_PATH)
    function_name = f"counter"
    args = (match_id,)

    try:
        manager = Web3HttpConnectionManager()
        data = await manager.fetch_contract_data(address, abi, function_name, *args)
        return data
    except Exception as e:
        logger.error(f"Unknown Error Occured: {e}")

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
