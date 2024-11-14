from web3 import Web3, AsyncWeb3, AsyncHTTPProvider

from ...logger import logging
from ...config import settings

logger = logging.getLogger(__name__)

http_uri = settings.ALCHEMY_API_HTTP_URI
api_key = settings.ALCHEMY_API_KEY

class Web3HttpConnectionManager:
    """Singleton for Web3 async connection to Provider."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.w3 = AsyncWeb3(AsyncHTTPProvider(f"{http_uri}{api_key}"))
        return cls._instance

    async def fetch_contract_data(self, contract_address: str, abi: list, function_name: str, *args):
        """
        Fetch data asynchronously from a blockchain by calling a specified function on a contract.
        
        :param contract_address: str - The address of the smart contract.
        :param abi: list - The ABI of the smart contract.
        :param function_name: str - The name of the function to call.
        :param args: tuple - Arguments to pass to the contract function.
        :return: The data returned by the smart contract function.
        """
        try:
            if not await self.w3.is_connected():
                raise ConnectionError("Could not connect to the blockchain.")
            
            contract = self.w3.eth.contract(address=self.w3.to_checksum_address(contract_address), abi=abi)

            contract_function = getattr(contract.functions, function_name)(*args)
            data = await contract_function.call()

            return data

        except Exception as e:
            logger.error(f"Error fetching contract data: {e}")
            return None
