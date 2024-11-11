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

