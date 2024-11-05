from arq.connections import RedisSettings
from arq.cron import cron

from ...core.config import settings
from .functions import (
    sample_background_task,
    shutdown,
    startup,
    process_data,
    call_usdtv1_arb_alchemy_fallback
)

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT

class WorkerSettings:
    functions = [
        sample_background_task,
        call_usdtv1_arb_alchemy_fallback

    ]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False

    cron_jobs = [
        cron(
            process_data,
            name="Process Data Cron",
            minute={0, 10, 20, 30, 40, 50},
            run_at_startup=True,
            timeout=600,
            max_tries=1
        )
    ]