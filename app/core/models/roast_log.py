"""
Pydantic data models for saving and retrieving roast logs.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.models.temp import TemperaturePoint
from app.core.models.markers import Marker
from app.core.models.crack import CrackStatus

class SaveRoastRequest(BaseModel):
    """Request model for saving roast data."""
    name: str = Field(default="Unnamed Roast", description="Name of the roast")
    profile: str = Field(default="Custom", description="Roast profile used")
    notes: Optional[str] = Field("", description="Notes about this roast")
    markers: Optional[List[Marker]] = Field(default_factory=list, description="Roast markers")
    crack_status: Optional[CrackStatus] = Field(None, description="Crack detection status")

        
class RoastSaveData(BaseModel):
    """Internal model for storing roast data."""
    name: str = Field(..., description="Name of the roast")
    timestamp: float = Field(..., description="Unix timestamp when saved")
    date: str = Field(..., description="Formatted date and time")
    profile: str = Field(..., description="Roast profile used")
    notes: Optional[str] = Field("", description="Notes about this roast")
    data: List[TemperaturePoint] = Field(..., description="Temperature data points")
    markers: Optional[List[Marker]] = Field(default_factory=list, description="Roast markers")
    crack_status: Optional[CrackStatus] = Field(None, description="Crack detection status")

    #first_crack_time: Optional[float] = Field(None, description="Time of first crack in seconds")
    #second_crack_time: Optional[float] = Field(None, description="Time of second crack in seconds")
    

class RoastLog(RoastSaveData):
    """Complete roast log with all data."""
    id: str = Field(..., description="Unique identifier for the roast")




##todo remove maybe?
class RoastLogSummary(BaseModel):
    """Summary information about a roast log."""
    id: str = Field(..., description="Unique identifier for the roast")
    name: str = Field(..., description="Name of the roast")
    date: str = Field(..., description="Date when the roast occurred")
    profile: str = Field(..., description="Roast profile used")
    duration: float = Field(..., description="Total duration in seconds")
    max_temp: float = Field(..., description="Maximum temperature reached")
    