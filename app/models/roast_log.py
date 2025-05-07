# app/core/models/roast_log.py
"""
Pydantic data models for saving and retrieving roast logs.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.temp import TemperaturePoint
from app.models.markers import RoastMarker

class SaveRoastRequest(BaseModel):
    """Request model for saving roast data."""
    name: str = Field(default="Unnamed Roast", description="Name of the roast")
    profile: str = Field(default="Custom", description="Roast profile used")
    notes: Optional[str] = Field("", description="Notes about this roast")
    filename: Optional[str] = Field(None, description="Filename to save as (optional)")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Ethiopian Yirgacheffe Light",
                "profile": "Light City",
                "notes": "Great floral notes, stopped just after first crack",
                "filename": "ethiopian_20240507"
            }
        }
        
        
class RoastSaveData(BaseModel):
    """Internal model for storing roast data."""
    timestamp: float = Field(..., description="Unix timestamp when saved")
    date: str = Field(..., description="Formatted date and time")
    name: str = Field(..., description="Name of the roast")
    profile: str = Field(..., description="Roast profile used")
    notes: str = Field(default="", description="Notes about this roast")
    data: List[Dict[str, float]] = Field(..., description="Temperature data points")
    markers: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Roast markers")
    first_crack_time: Optional[float] = Field(None, description="Time of first crack in seconds")
    second_crack_time: Optional[float] = Field(None, description="Time of second crack in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "timestamp": 1651929600,
                "date": "2024-05-07 14:30:00",
                "name": "Ethiopian Yirgacheffe Light",
                "profile": "Light City",
                "notes": "Great floral notes, stopped just after first crack",
                "data": [
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
                "first_crack_time": 360.5,
                "second_crack_time": None
            }
        }

class RoastLog(BaseModel):
    """Complete roast log with all data."""
    id: str = Field(..., description="Unique identifier for the roast")
    name: str = Field(..., description="Name of the roast")
    date: str = Field(..., description="Date when the roast occurred")
    profile: str = Field(..., description="Roast profile used")
    duration: float = Field(..., description="Total duration in seconds")
    data: List[TemperaturePoint] = Field(..., description="Temperature data points")
    markers: List[RoastMarker] = Field(default_factory=list, description="Roast markers")
    notes: Optional[str] = Field("", description="Notes about this roast")
    first_crack_time: Optional[float] = Field(None, description="Time of first crack in seconds")
    second_crack_time: Optional[float] = Field(None, description="Time of second crack in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "roast-12345",
                "name": "Ethiopian Yirgacheffe Light",
                "date": "2024-05-07 14:30:00",
                "profile": "Light City",
                "duration": 720.0,
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
                "notes": "Great floral notes, stopped just after first crack",
                "first_crack_time": 360.5,
                "second_crack_time": None
            }
        }

class RoastLogSummary(BaseModel):
    """Summary information about a roast log."""
    id: str = Field(..., description="Unique identifier for the roast")
    name: str = Field(..., description="Name of the roast")
    date: str = Field(..., description="Date when the roast occurred")
    profile: str = Field(..., description="Roast profile used")
    duration: float = Field(..., description="Total duration in seconds")
    max_temp: float = Field(..., description="Maximum temperature reached")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "roast-12345",
                "name": "Ethiopian Yirgacheffe Light",
                "date": "2024-05-07 14:30:00",
                "profile": "Light City",
                "duration": 720.0,
                "max_temp": 215.5
            }
        }