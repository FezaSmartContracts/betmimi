from datetime import datetime

def on_deposit_message(amount: float, balance: float) -> str:
    return (
        f"We are pleased to inform you that a deposit of ${amount:.2f} has been received. "
        f"Your current balance is now ${balance:.2f}. "
        "Thank you for trusting us with your transactions!"
    )

def on_game_register(game_id: int) -> str:
    return (
        f"Game with ID {game_id} has been successfully registered and will start Soon. "
        "Stay tuned for updates!"
    )

def on_game_reslution(game_id: int) -> str:
    return (
        f"Game with ID {game_id} has been resolved. "
        "Stay tuned for updates!"
    )

def on_withdrawal_message(amount: float, balance: float) -> str:
    return (
        f"A withdrawal of ${amount:.2f} has been processed successfully. "
        f"Your remaining balance is ${balance:.2f}. "
        "If you have any questions, please feel free to reach out to us."
    )

def on_lay(amount: float) -> str:
    return (
        f"Your lay prediction of {amount} USDT has been successfully processed. "
        "If you have any questions, please feel free to reach out to us."
    )

def support_link() -> str:
    return "https://discord.gg/REJHCvre"

def on_revenue_withdrawal(amount: float, address: str, email: str) -> str:
    return (
        f"A revenue withdrawal of ${amount:.2f} has been processed successfully by;\n"
        f"- Wallet Address: {address}\n"
        f"- Email: {email}\n\n"
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_admin_added(admin: str, contract_address: str) -> str:
    return (
        f"A new Admin {admin} has been added for contract: {contract_address} . "
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_admin_removed(admin: str, contract_address: str) -> str:
    return (
        f"Admin status for {admin} for contract {contract_address} has been revoked! . "
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_whitlist(admin: str, contract_address: str, by: str) -> str:
    return (
        f"A new Address {admin} has been whitelisted for contract: {contract_address} by {by}. "
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_blacklist(admin: str, contract_address: str, by: str) -> str:
    return (
        f"A new Address {admin} has been blacklisted for contract: {contract_address} by {by}. "
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_fee_change(new_percentage: int, contract_address: str) -> str:
    return (
        f"Contract {contract_address} charrge fees changed to {new_percentage}. "
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_ownership_transfer_initiation(current: str, future: str, contract_address: str) -> str:
    return (
        f"Ownership transfer for contract: {contract_address} initiated. \n"
        f"- Current Owner: {current} \n"
        f"- Future owner: {future} \n"
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_ownership_transfer_completion(current: str, prev: str, contract_address: str) -> str:
    return (
        f"Ownership transfer for contract: {contract_address} completed. \n"
        f"- Current Owner: {current} \n"
        f"- previous owner: {prev} \n"
        "If you find this activity suspicious, please report it to our team immediately."
    )

def on_pred_settlement(match_id: int) -> str:
    f"Your Prediction on Game {match_id} has been Settled.\n"
    "If you have any questions, please feel free to reach out to us."