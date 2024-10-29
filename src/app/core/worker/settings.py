from arq.connections import RedisSettings
from arq.cron import cron

from ...core.config import settings
from ...core.db.database import async_get_db
from .functions import (
    sample_background_task,
    shutdown,
    startup,
    subscribe_to_winorloss_arb_usdtv1_events,
    process_data
)

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT


class WorkerSettings:
    functions = [
        sample_background_task,
        subscribe_to_winorloss_arb_usdtv1_events
    ]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False
    job_timeout = 120 # 2 minutes

    cron_jobs = [
        cron(
            process_data,
            name="Process Data Cron",
            minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55},
            run_at_startup=True,
            timeout=300,
            max_tries=1
        )
    ]