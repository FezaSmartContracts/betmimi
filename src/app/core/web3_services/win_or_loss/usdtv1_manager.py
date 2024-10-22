import asyncio
import json
import websockets
from fastapi import FastAPI
from web3 import AsyncWeb3, WebSocketProvider
from eth_abi import decode
from ...config import settings

API_KEY = settings.ALCHEMY_API_KEY

def usdtv1_abi():
    """Fetch contract ABI"""
    with open("src/app/core/artifacts/USDTv1.json", "r") as file:
        return json.load(file)

def contract_address(key):
    """Fetch contract address"""
    with open('src/app/core/artifacts/deployments.json', 'r') as file:
        contracts = json.load(file)
    if key in contracts:
        return contracts[key]['contract_address']
    else:
        raise ValueError(f"Contract with key {key} not found.")

CONTRACT_ADDRESS = contract_address("WinOrLoss")
PROVIDER_URI = f"wss://arb-sepolia.g.alchemy.com/v2/{API_KEY}"

async def subscribe_to_events():

    """
    - Subscribe to multiple USDTv1 contract events
    - The set up allows for indefinite websocket connection 
    - and reconnect automatically if the connection is lost.

    """

    async for w3 in AsyncWeb3(WebSocketProvider(PROVIDER_URI)):
        try:
            deposited_event_topic = w3.keccak(text="Deposited(address)")
            predicted_event_topic = w3.keccak(text="Predicted(uint256, address, uint256)")
            backed_event_topic = w3.keccak(text="Backed(uint256, address, uint256)")
            settled_event_topic = w3.keccak(text="PredictionSettled(uint256, uint256)")
            bet_sold_event_topic = w3.keccak(text="BetSold(uint256, uint256, address, address)")
            sell_initiated_event_topic = w3.keccak(text="BetSellInitiated(uint256, uint256, address)")
            price_changed_event_topic = w3.keccak(text="SellingPriceChanged(uint256, uint256)")

            filter_params = {
                "address": CONTRACT_ADDRESS,
                "topics": [
                    deposited_event_topic, predicted_event_topic, backed_event_topic, settled_event_topic,
                    bet_sold_event_topic, sell_initiated_event_topic, price_changed_event_topic
                ],
            }
            subscription_id = await w3.eth.subscribe("logs", filter_params)
            print(f"Subscribed to events at {subscription_id}")
                
            async for payload in w3.socket.process_subscriptions():
                result = payload["result"]

                # Identify the event by topic and process it
                event_topic = result["topics"][0]  # The event signature

                if event_topic == deposited_event_topic:
                    from_addr = decode(["address"], result["topics"][1])[0]
                    event_data = {"from_addr": from_addr}
                    print(f"Deposited Event from: {from_addr}")

                    # Update the database for Deposited event e.g;
                    # await update_database("Deposited", event_data)

                elif event_topic == predicted_event_topic:
                    # Similar decoding for Predicted event
                    game_id = decode(["uint256"], result["topics"][1])[0]
                    user = decode(["address"], result["topics"][2])[0]
                    amount = decode(["uint256"], result["data"])[0]
                    event_data = {"game_id": game_id, "user": user, "amount": amount}
                    print(f"Predicted Event: game_id={game_id}, user={user}, amount={amount}")

                    
                # Continue processing other events similarly...

        except websockets.ConnectionClosed:
            continue
