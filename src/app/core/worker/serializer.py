from typing import Any
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

def serialize_job_result(job_info: Any) -> dict[str, Any]:
    """Convert JobResult or similar object to a serializable dictionary."""
    if job_info:
        return {
            "function": job_info.function,
            "args": job_info.args,
            "kwargs": job_info.kwargs,
            "job_try": job_info.job_try,
            "enqueue_time": job_info.enqueue_time.isoformat() if isinstance(job_info.enqueue_time, datetime) else None,
            "start_time": job_info.start_time.isoformat() if isinstance(job_info.start_time, datetime) else None,
            "finish_time": job_info.finish_time.isoformat() if isinstance(job_info.finish_time, datetime) else None,
            "success": job_info.success,
            "result": job_info.result,
            "job_id": job_info.job_id,
            "queue_name": job_info.queue_name,
        }
    return {}

def serialize_job_results(job_info: Any) -> dict[str, Any]:
    """Convert JobResult or similar object to a serializable dictionary."""
    if job_info:
        # Check if the result contains an exception like TimeoutError
        result = job_info.result
        if isinstance(result, Exception):
            result = {
                "error": str(result),  # Convert the exception to a string
                "error_type": type(result).__name__,  # Include the exception type
            }
        return {
            "function": job_info.function,
            "args": job_info.args,
            "kwargs": job_info.kwargs,
            "job_try": job_info.job_try,
            "enqueue_time": job_info.enqueue_time.isoformat() if isinstance(job_info.enqueue_time, datetime) else None,
            "start_time": job_info.start_time.isoformat() if isinstance(job_info.start_time, datetime) else None,
            "finish_time": job_info.finish_time.isoformat() if isinstance(job_info.finish_time, datetime) else None,
            "success": job_info.success,
            "result": result,  # Use the updated result
            "job_id": job_info.job_id,
            "queue_name": job_info.queue_name,
        }
    return {}