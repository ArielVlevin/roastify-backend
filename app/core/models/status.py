"""
Pydantic data models for roaster status.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.models.temp import TemperaturePoint
from app.core.models.markers import Marker
from app.core.models.crack import CrackStatus

class RoastStatus(BaseModel):
    """Current status of the roaster."""
    is_roasting: bool = Field(..., description="Whether roasting is active")
    temperature: float = Field(..., description="Current temperature in Celsius")
    elapsed_time: float = Field(..., description="Elapsed time in seconds")
    roast_stage: str = Field(..., description="Current roast stage")
    crack_status: CrackStatus = Field(..., description="Crack detection status")

class RoastSession(BaseModel):
    """Complete roast session data."""
    is_roasting: bool = Field(..., description="Whether roasting is active")
    start_time: float = Field(..., description="Start time as Unix timestamp")
    elapsed_time: float = Field(..., description="Elapsed time in seconds")
    temperature_data: List[TemperaturePoint] = Field(default_factory=list, description="Temperature data points")
    markers: List[Marker] = Field(default_factory=list, description="Roast markers")
    crack_status: CrackStatus = Field(..., description="Crack detection status")