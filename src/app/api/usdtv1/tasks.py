from typing import Any, Optional, Dict

from fastapi import HTTPException
from arq.jobs import Job as ArqJob
from fastapi import APIRouter, Depends
from datetime import datetime

from ...api.dependencies import rate_limiter
from ...core.utils import queue
from ...models.job import Job

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
@router.post("/task", response_model=Dict[str, str], status_code=201)
async def create_task(message: str, from_block: int, to_block: int) -> Dict[str, str]:
    """Create a new background task.

    Parameters
    ----------
    message: str
        The message or data to be processed by the task.
    from_block: int
        The starting block number for fetching logs.
    to_block: int
        The ending block number for fetching logs.

    Returns
    -------
    dict[str, str]
        A dictionary containing the ID of the created task.
    """
    try:
        job = await queue.pool.enqueue_job(
            "call_usdtv1_arb_alchemy_callback",
            message,  # `message` as the task name
            from_block,
            to_block
        )
        return {"id": job.job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

