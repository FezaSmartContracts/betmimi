from fastapi import APIRouter

from app.api.general.connect_wallet import router as connect_router
from app.api.general.disconnect_wallet import router as disconnect_router
from app.api.general.rate_limits import router as rate_limits_router
from app.api.general.users import router as users_router
from app.api.general.admin import router as admin_router
from app.api.general.games import router as games_router

router = APIRouter(prefix="/v1")
router.include_router(connect_router)
router.include_router(disconnect_router)
router.include_router(users_router)
router.include_router(rate_limits_router)
router.include_router(admin_router)
router.include_router(games_router)
