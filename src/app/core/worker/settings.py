from arq.connections import RedisSettings

from ...core.config import settings
from .functions import (
    sample_background_task,
    shutdown,
    startup,
    subscribe_to_events
)

REDIS_QUEUE_HOST = settings.REDIS_QUEUE_HOST
REDIS_QUEUE_PORT = settings.REDIS_QUEUE_PORT


class WorkerSettings:
    functions = [sample_background_task, subscribe_to_events]
    redis_settings = RedisSettings(host=REDIS_QUEUE_HOST, port=REDIS_QUEUE_PORT)
    on_startup = startup
    on_shutdown = shutdown
    handle_signals = False
    job_timeout = 120 # 2 minutes