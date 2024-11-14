
ALCHEMY_REDIS_QUEUE_NAME = f"alchemy_logs_queue"
ALCHEMY_INPROCESSING_QUEUE = f"alchemy_inprocessing_queue"
ALCHEMY_SUBSCRIPTIONS_QUEUE_NAME = f"subscriptions_queue"
MAIL_QUEUE = f"mails_queue"
ALERTS_QUEUE = f"alerts_queue"
USER_NAME = f"Mimion"

#------------mail event-specific queue names-----
def game_registered_notify() -> str:
    subject = f"New Game registered!"
    queue_name = MAIL_QUEUE
    return subject, queue_name

def game_resolved_notify() -> str:
    subject = f"Game resolved!"
    queue_name = MAIL_QUEUE
    return subject, queue_name

def lay_notify() -> str:
    subject = f"Lay Successful."
    queue_name = MAIL_QUEUE
    return subject, queue_name

def pred_settled_notify() -> str:
    subject = f"Prediction settled."
    queue_name = MAIL_QUEUE
    return subject, queue_name

def revenue_alert() -> str:
    subject = f"Revenue Withdrawn!!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def admin_added_alert() -> str:
    subject = f"New Contract Admin Added!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def admin_removed_alert() -> str:
    subject = f"Contract Admin Removed!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def ownership_transfer_initiation_alert() -> str:
    subject = f"New Ownership Transfer Initiated!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def ownership_transfer_completed_alert() -> str:
    subject = f"New Ownership Transfer Completed!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def charge_fees_changed_alert() -> str:
    subject = f"Charge fees adjusted!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def address_added_to_whiteliist_alert() -> str:
    subject = f"New Contract Address added to whitelist!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def address_removed_from_whiteliist_alert() -> str:
    subject = f"New Contract Address removed from whitelist!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def websocket_disconnected() -> str:
    subject = f"ALERT!!! Websocket disconnected!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name

def websocket_reconnected() -> str:
    subject = f"ALERT!! Websocket Re-connected!"
    queue_name = ALERTS_QUEUE
    return subject, queue_name