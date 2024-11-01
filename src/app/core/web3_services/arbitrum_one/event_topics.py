from typing import Dict, Annotated
from decimal import Decimal, ROUND_DOWN
from hexbytes import HexBytes
from eth_abi.abi import decode
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..utils import load_abi, get_event_topic
from ...logger import logging


logger = logging.getLogger(__name__)

USDTV1_ABI_PATH = "../artifacts/arbitrum/USDTv1.json"

def usdtv1_event_topics_dict() -> Dict[str, HexBytes]:
    """Constructs a dictionary of event topics for USDTv1 events."""
    try:
        ABI = load_abi(USDTV1_ABI_PATH)
        return {
            "Deposited": get_event_topic(ABI, "Deposited"),
            "Predicted": get_event_topic(ABI, "Predicted"),
            "Backed": get_event_topic(ABI, "Backed"),
            "Claimed": get_event_topic(ABI, "Claimed"),
            "GameRegistered": get_event_topic(ABI, "GameRegistered"),
            "PredictionSettled": get_event_topic(ABI, "PredictionSettled"),
            "BetSold": get_event_topic(ABI, "BetSold"),
            "BetSellInitiated": get_event_topic(ABI, "BetSellInitiated"),
            "SellingPriceChanged": get_event_topic(ABI, "SellingPriceChanged")
        }
    except Exception as e:
        logger.error(f"Failed to construct event topics dictionary: {e}")
        return {}