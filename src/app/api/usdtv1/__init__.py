from fastapi import APIRouter

from app.api.usdtv1.predictions import router as all_predictions_router
from app.api.usdtv1.tasks import router as tasks_router

router = APIRouter(prefix="/v1")

router.include_router(all_predictions_router)
router.include_router(tasks_router)