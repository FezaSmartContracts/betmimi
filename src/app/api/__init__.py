from fastapi import APIRouter

from ..api.general import router as general_router
from ..api.usdtv1 import router as usdtv1

router = APIRouter(prefix="/api")
router.include_router(general_router)
router.include_router(usdtv1)
