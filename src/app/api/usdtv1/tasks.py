from typing import Any, Optional

from arq.jobs import Job as ArqJob
from fastapi import APIRouter, Depends
from datetime import datetime

from ...api.dependencies import rate_limiter
from ...core.utils import queue
from ...models.job import Job
from ...core.worker.serializer import serialize_job_result, serialize_job_results

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/task/{task_id}")
async def get_task(task_id: str) -> dict[str, Any] | None:
    """Get information about a specific background task.

    Parameters
    ----------
    task_id: str
        The ID of the task.

    Returns
    -------
    Optional[dict[str, Any]]
        A dictionary containing information about the task if found, or None otherwise.
    """
    job = ArqJob(task_id, queue.pool)
    job_info: dict = await job.info()
    if job_info:
        return vars(job_info)
    
    return None

#dependencies=[Depends(rate_limiter)]
@router.post("/task", response_model=Job, status_code=201)
async def create_task(message: str) -> dict[str, str]:
    """Create a new background task.

    Parameters
    ----------
    message: str
        The message or data to be processed by the task.

    Returns
    -------
    dict[str, str]
        A dictionary containing the ID of the created task.
    """
    job = await queue.pool.enqueue_job("process_data", message)  # type: ignore
    return {"id": job.job_id}

@router.post("/tasks", response_model=Job, status_code=201)
async def create_tasks(message: str) -> dict[str, str]:
    """Create a new background task.

    Parameters
    ----------
    message: str
        The message or data to be processed by the task.

    Returns
    -------
    dict[str, str]
        A dictionary containing the ID of the created task.
    """
    job = await queue.pool.enqueue_job("process_event", message)  # type: ignore
    return {"id": job.job_id}
