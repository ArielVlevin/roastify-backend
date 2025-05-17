"""
Router initialization for API endpoints.
"""
from fastapi import APIRouter

api_router = APIRouter(prefix="/api")

from .roast_control import router as control_router
from .roast_data import router as data_router
from .roast_status import router as status_router
from .log import router as log_router

api_router.include_router(control_router)
api_router.include_router(data_router)
api_router.include_router(status_router)
api_router.include_router(log_router)
