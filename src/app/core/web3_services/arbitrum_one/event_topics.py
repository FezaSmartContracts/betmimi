from typing import Dict
from hexbytes import HexBytes

from app.core.web3_services.utils import load_abi, get_event_topic
from ...logger import logging


logger = logging.getLogger(__name__)

USDTV1_ABI_PATH = "../artifacts/arbitrum/USDTv1.json"
BALANCE_USDT_ABI_PATH = "../artifacts/arbitrum/UsdtManager.json"
GAMES_MANAGER = "../artifacts/arbitrum/GamesManager.json"

def usdtv1_event_topics_dict() -> Dict[str, HexBytes]:
    """Constructs a dictionary of event topics for USDTv1 events."""
    try:
        USDTV1_ABI = load_abi(USDTV1_ABI_PATH)
        BALANCE_ABI = load_abi(BALANCE_USDT_ABI_PATH)
        GAMES_ABI = load_abi(GAMES_MANAGER)
        return {
            "Deposited": get_event_topic(BALANCE_ABI, "Deposited"),
            "Predicted": get_event_topic(USDTV1_ABI, "Predicted"),
            "Backed": get_event_topic(USDTV1_ABI, "Backed"),
            "Claimed": get_event_topic(BALANCE_ABI, "Claimed"),
            "GameRegistered": get_event_topic(GAMES_ABI, "GameRegistered"),
            "PredictionSettled": get_event_topic(USDTV1_ABI, "PredictionSettled"),
            "BetSold": get_event_topic(USDTV1_ABI, "BetSold"),
            "BetSellInitiated": get_event_topic(USDTV1_ABI, "BetSellInitiated"),
            "SellingPriceChanged": get_event_topic(USDTV1_ABI, "SellingPriceChanged"),
            "GameResolved": get_event_topic(GAMES_ABI, "GameResolved"),
            "UserBalance": get_event_topic(USDTV1_ABI, "UserBalance"),
            "ReceivedFallback": get_event_topic(USDTV1_ABI, "ReceivedFallback"),
            "EtherWithdrawn": get_event_topic(BALANCE_ABI, "EtherWithdrawn"),
            "RevenueWithdrawn": get_event_topic(BALANCE_ABI, "RevenueWithdrawn")
        }
    except Exception as e:
        logger.error(f"Failed to construct event topics dictionary: {e}")
        return {}