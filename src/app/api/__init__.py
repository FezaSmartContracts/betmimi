from fastapi import APIRouter

from ..api.general import router as general_router

router = APIRouter(prefix="/api")
router.include_router(general_router)
