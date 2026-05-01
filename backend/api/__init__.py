"""
api module

Holds code for api endpoints and modules

Exports `router` with all api routes.
"""

__all__ = ["router"]

from fastapi import APIRouter

from .achievements import router as achievements_router
from .auth import router as auth_router
from .logs import router as logs_router
from .notes import router as notes_router
from .plants import router as plants_router
from .sensors import router as sensors_router

router = APIRouter(
    prefix="/api",
    tags=["api"],
)

router.include_router(auth_router, tags=["auth"])
router.include_router(logs_router, tags=["logs"])
router.include_router(notes_router, tags=["notes"])
router.include_router(plants_router, tags=["plants"])
router.include_router(sensors_router, tags=["sensors"])
router.include_router(achievements_router, tags=["achievements"])
