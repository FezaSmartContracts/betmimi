from arq.connections import RedisSettings
from arq.cron import cron

from app.core.config import settings
from app.core.worker.functions import (
    sample_background_task,
    shutdown,
    startup,
    process_data,
    call_usdtv1_arb_alchemy_fallback,
    send_email,
    send_email_manually
)

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT

two_minute_squenece = {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 58}
three_minute_squence = {0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57}
five_minute_squence = {0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}
one_minute_sequence = {i for i in range(60)}

class WorkerSettings:
    functions = [
        sample_background_task,
        call_usdtv1_arb_alchemy_fallback,
        send_email_manually
    ]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False

    cron_jobs = [
        cron(
            process_data,
            name="Process Data Cron",
            minute=three_minute_squence,
            run_at_startup=True,
            timeout=180,
            max_tries=1
        ),
        cron(
            send_email,
            name="Automatic Emailing Cron",
            minute=one_minute_sequence,
            run_at_startup=False,
            timeout=60,
            max_tries=1
        )
    ]