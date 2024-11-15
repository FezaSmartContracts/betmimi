from typing import Dict

from fastapi import HTTPException
from fastapi import APIRouter, Depends

from ...api.dependencies import rate_limiter, get_admin
from ...core.utils import queue
from ...models.job import Job
from ...schemas.job import ArbUsdtv1FallBack

router = APIRouter(prefix="/tasks", tags=["tasks"])



@router.post(
    "/usdtv1/task",
    response_model=Job,
    status_code=201,
    #dependencies=[
    #    Depends(get_admin),
    #    Depends(rate_limiter)
    #]
)
async def create_fall_back_task(params: ArbUsdtv1FallBack) -> Dict[str, str]:
    """Create a new background task. Creates a task for fetching missed event logs during network downtimes.

    Specific to `arbitrum-one, USDT`

    Parameters
    ---------
    - `name: str`
        The message/name or data to be processed by the task.
    - `from_block: int`
        The starting block number for fetching logs.
    - `to_block: int`
        The ending block number for fetching logs.

    Note:
    -----
    - Restricted to be called by only users with admin previlages.

    Returns
    -------
    - `dict[str, str]`
        A dictionary containing the ID of the created task.
    """
    try:
        job = await queue.pool.enqueue_job(
            "call_usdtv1_arb_alchemy_fallback",
            params.name,
            params.from_block,
            params.to_block
        )
        return {"id": job.job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")

@router.post(
    "/email-task",
    response_model=Job,
    status_code=201,
    #dependencies=[
    #    Depends(get_admin),
    #    Depends(rate_limiter)
    #]
)
async def create_email_task(message: str) -> dict[str, str]:
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
    job = await queue.pool.enqueue_job("send_email_manually", message)  # type: ignore
    return {"id": job.job_id}

#------------For testing purposes------------
@router.post("/task", response_model=Job, status_code=201, dependencies=[Depends(rate_limiter)])
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
    job = await queue.pool.enqueue_job("sample_background_task", message)  # type: ignore
    return {"id": job.job_id}

