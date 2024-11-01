from typing import Dict

from .handlers.usdtv1 import (
    process_usdtv1_deposits,
    process_usdtv1_backs,
    process_usdtv1_lays,
    process_usdtv1_bet_sell_initiated,
    process_usdtv1_bet_sold,
    process_usdtv1_selling_price_changed,
    process_usdtv1_settled_pred,
    process_usdtv1_claims,
    register_games
)


def usdtv1_event_handlers() -> Dict[str, callable]:
    """Maps events to their respective handler functions."""
    return {
        "Deposited": process_usdtv1_deposits,
        "Predicted": process_usdtv1_lays,
        "Backed": process_usdtv1_backs,
        "Claimed": process_usdtv1_claims,
        "BetSellInitiated": process_usdtv1_bet_sell_initiated,
        "BetSold": process_usdtv1_bet_sold,
        "SellingPriceChanged": process_usdtv1_selling_price_changed,
        "PredictionSettled": process_usdtv1_settled_pred,
        "GameRegistered": register_games
    }
