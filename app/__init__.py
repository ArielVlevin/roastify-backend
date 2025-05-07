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
from app.models.temp import TemperaturePoint
from app.models.markers import RoastMarker
from app.models.crack import CrackStatus
from app.models.status import RoastStatus, RoastSession
from app.models.responses import (
    TemperatureResponse, 
    StatusResponse, 
    MessageResponse, 
    RoastStartResponse
)
from app.models.roast_log import (
    SaveRoastRequest, 
    RoastLog, 
    RoastLogSummary,
    RoastSaveData
)

__all__ = [
    "TemperaturePoint",
    "TemperatureResponse",
    "StatusResponse",
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
from app.api import roast, logs

__all__ = ["roast", "logs"]

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