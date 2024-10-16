from typing import Any
from fastapi import HTTPException
from eth_account.messages import encode_defunct
from web3.auto import w3
import uuid

def generate_random():
    """Generate a random UUID and return the first 4 characters."""
    return str(uuid.uuid4())[:4]


def verify_signature(nonce: str, public_address: str, signature: str) -> bool:
    """
    Verify the given signature against the provided nonce.
    Args:
        nonce (str): The nonce string.
        signature (str): The signature string.
    Returns:
        bool: True if the signature is valid, otherwise raises HTTPException.
    """
    # # Here nonce is signed directly, change it if the frontend is signing a different format;
    # message = encode_defunct(f"Your Secure Login Code: {nonce}")
    message = encode_defunct(text=nonce)
    try:
        recovered_address = w3.eth.account.recover_message(message, signature=signature)
        if str(recovered_address).lower() != public_address.lower():
            raise HTTPException(status_code=400, detail="Invalid signature")
        return True
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")