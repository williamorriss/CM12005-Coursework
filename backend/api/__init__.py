__all__ = ["router", "authorize"]

from .auth import authorize


from fastapi import APIRouter
from .auth import router as auth_router
from .logs import router as log_router
from .notes import router as notes_router
from .logs import router as logs_router
from .sensors import router as sensors_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(sensors_router)
router.include_router(logs_router)
router.include_router(notes_router)
router.include_router(sensors_router)