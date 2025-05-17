# app/__init__.py
"""
Coffee Roaster API application.
"""
from app.main import app, start

__all__ = ["app", "start"]

# app/models/__init__.py
"""
Pydantic models for the Coffee Roaster API.
"""
from app.core.models.temp import TemperaturePoint
from app.core.models.markers import Marker
from app.core.models.crack import CrackStatus
from app.core.models.status import RoastStatus, RoastSession
from app.core.models.responses import (
    TemperatureResponse, 
    MessageResponse, 
    RoastStartResponse
)
from app.core.models.roast_log import (
    SaveRoastRequest, 
    RoastLog, 
    RoastLogSummary,
    RoastSaveData
)

__all__ = [
    "TemperaturePoint",
    "TemperatureResponse",
    "RoastStartResponse",
    "SaveRoastRequest",
    "MessageResponse",
    "RoastLog",
    "RoastSaveData"
]

# app/api/__init__.py
"""
API routes for the Coffee Roaster API.
"""
from app.api.router import api_router

__all__ = ["api_router"]

# app/core/__init__.py
"""
Core functionality for the Coffee Roaster API.
"""
from app.core import hardware, simulator

__all__ = ["hardware", "simulator"]

# app/services/__init__.py
"""
Services for the Coffee Roaster API.
"""
from app.core import storage,monitor

__all__ = ["monitor", "storage"]