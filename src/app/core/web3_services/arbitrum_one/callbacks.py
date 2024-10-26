from hexbytes import HexBytes

from ..utils import (
    load_abi,
    get_event_topic
)

async def process_winorloss_callbacklogs(message):
    """Callback function for Updating/persisting data to database"""
    try:
        abi_relative_path = "../artifacts/arbitrum/usdtv1.json"
        ABI = load_abi(abi_relative_path)
        payload = message['result']
        event_signature: HexBytes = payload['topics'][0]

        event_topics = {
            "Deposited": get_event_topic(ABI, "Deposited"),
            "Predicted": get_event_topic(ABI, "Predicted"),
            "Backed": get_event_topic(ABI, "Backed"),
            "Claimed": get_event_topic(ABI, "Claimed"),
            "GameRegistered": get_event_topic(ABI, "GameRegistered"),
            "GameResolved": get_event_topic(ABI, "GameResolved"),
            "PredictionSettled": get_event_topic(ABI, "PredictionSettled"),
            "ReceivedFallback": get_event_topic(ABI, "ReceivedFallback"),
            "BetSold": get_event_topic(ABI, "BetSold"),
            "BetSellInitiated": get_event_topic(ABI, "BetSellInitiated"),
            "SellingPriceChanged": get_event_topic(ABI, "SellingPriceChanged")
        }


        deposit_topic = get_event_topic(ABI, "Deposited")
        lay_topic = get_event_topic(ABI, "Predicted")
        back_topic = get_event_topic(ABI, "Backed")
        withdraw_topic = get_event_topic(ABI, "Claimed")
        game_register_topic = get_event_topic(ABI, "GameRegistered")
        resolve_topic = get_event_topic(ABI, "GameResolved")
        pred_settled_topic = get_event_topic(ABI, "PredictionSettled")
        fallback_topic = get_event_topic(ABI, "ReceivedFallback")
        bet_sold_topic = get_event_topic(ABI, "BetSold")
        sale_init_topic = get_event_topic(ABI, "BetSellInitiated")
        price_changed_topic = get_event_topic(ABI, "SellingPriceChanged")

        if deposit_topic == event_signature:
            pass
        elif lay_topic == event_signature:
            pass
        elif back_topic == event_signature:
            pass
        elif withdraw_topic == event_signature:
            pass
        elif game_register_topic == event_signature:
            pass
        elif resolve_topic == event_signature:
            pass
        elif pred_settled_topic == event_signature:
            pass
        elif bet_sold_topic == event_signature:
            pass
        elif sale_init_topic == event_signature:
            pass
        elif price_changed_topic == event_signature:
            pass
        elif fallback_topic == event_signature:
            pass
        else:
            raise RuntimeError("Event Log can't be identified!")

    except Exception as e:
        pass