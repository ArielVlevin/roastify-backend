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
from app.models.schemas import (
    TemperaturePoint,
    TemperatureResponse,
    StatusResponse,
    HeatLevelRequest,
    RoastStartResponse,
    SaveRoastRequest,
    MessageResponse,
    RoastLog,
    RoastSaveData
)

__all__ = [
    "TemperaturePoint",
    "TemperatureResponse",
    "StatusResponse",
    "HeatLevelRequest",
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
from app.services import monitoring, storage

__all__ = ["monitoring", "storage"]