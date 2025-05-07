"""
Pydantic data models for roaster status.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.temp import TemperaturePoint
from app.models.markers import RoastMarker
from app.models.crack import CrackStatus

class RoastStatus(BaseModel):
    """Current status of the roaster."""
    is_roasting: bool = Field(..., description="Whether roasting is active")
    temperature: float = Field(..., description="Current temperature in Celsius")
    elapsed_time: float = Field(..., description="Elapsed time in seconds")
    roast_stage: str = Field(..., description="Current roast stage")
    crack_status: CrackStatus = Field(..., description="Crack detection status")
    
    class Config:
        schema_extra = {
            "example": {
                "is_roasting": True,
                "temperature": 190.5,
                "elapsed_time": 420.0,
                "roast_stage": "Light Brown",
                "crack_status": {
                    "first": True,
                    "second": False,
                    "first_time": 360.5,
                    "second_time": None
                }
            }
        }

class RoastSession(BaseModel):
    """Complete roast session data."""
    is_roasting: bool = Field(..., description="Whether roasting is active")
    start_time: float = Field(..., description="Start time as Unix timestamp")
    elapsed_time: float = Field(..., description="Elapsed time in seconds")
    temperature_data: List[TemperaturePoint] = Field(default_factory=list, description="Temperature data points")
    markers: List[RoastMarker] = Field(default_factory=list, description="Roast markers")
    crack_status: CrackStatus = Field(..., description="Crack detection status")
    
    class Config:
        schema_extra = {
            "example": {
                "is_roasting": True,
                "start_time": 1619712000,
                "elapsed_time": 420.0,
                "temperature_data": [
                    {"time": 0.0, "temperature": 25.0},
                    {"time": 60.0, "temperature": 100.0}
                ],
                "markers": [
                    {
                        "id": "marker-12345",
                        "time": 360.0,
                        "temperature": 190.5,
                        "label": "First Crack",
                        "color": "#FF5733",
                        "notes": "First crack detected"
                    }
                ],
                "crack_status": {
                    "first": True,
                    "second": False,
                    "first_time": 360.5,
                    "second_time": None
                }
            }
        }