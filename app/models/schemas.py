"""
Pydantic data models for the Coffee Roaster API.
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

class TemperaturePoint(BaseModel):
    """Represents a single temperature data point."""
    time: float = Field(..., description="Time in minutes from start of roast")
    temperature: float = Field(..., description="Temperature in Fahrenheit")

class TemperatureResponse(BaseModel):
    """Response model for temperature endpoint."""
    temperature: float = Field(..., description="Current temperature in Fahrenheit")
    timestamp: float = Field(..., description="Unix timestamp of the reading")

class StatusResponse(BaseModel):
    """Response model for roaster status."""
    is_roasting: bool = Field(..., description="Whether roasting is currently active")
    heat_level: int = Field(..., description="Current heat level (1-10)")
    temperature: float = Field(..., description="Current temperature in Fahrenheit")
    elapsed_time: float = Field(..., description="Elapsed time in minutes")

class HeatLevelRequest(BaseModel):
    """Request model for setting heat level."""
    level: int = Field(..., ge=1, le=10, description="Heat level (1-10)")

class RoastStartResponse(BaseModel):
    """Response model for starting a roast."""
    message: str = Field(..., description="Status message")
    time: float = Field(..., description="Start time as Unix timestamp")

class SaveRoastRequest(BaseModel):
    """Request model for saving roast data."""
    name: str = Field(default="Unnamed Roast", description="Name of the roast")
    profile: str = Field(default="Custom", description="Roast profile used")
    notes: Optional[str] = Field(default="", description="Notes about this roast")
    filename: Optional[str] = Field(default=None, description="Filename to save as (optional)")

class MessageResponse(BaseModel):
    """Generic response with a message."""
    message: str = Field(..., description="Response message")

class RoastLog(BaseModel):
    """Complete roast log with all data."""
    id: str = Field(..., description="Unique identifier for the roast")
    name: str = Field(..., description="Name of the roast")
    date: str = Field(..., description="Date when the roast occurred")
    profile: str = Field(..., description="Roast profile used")
    duration: float = Field(..., description="Total duration in minutes")
    tempData: List[Dict[str, float]] = Field(..., description="Temperature data points")
    notes: Optional[str] = Field(default="", description="Notes about this roast")
    firstCrack: Optional[float] = Field(default=None, description="Time of first crack in minutes")
    secondCrack: Optional[float] = Field(default=None, description="Time of second crack in minutes")

class RoastSaveData(BaseModel):
    """Internal model for storing roast data."""
    timestamp: float = Field(..., description="Unix timestamp when saved")
    date: str = Field(..., description="Formatted date and time")
    name: str = Field(..., description="Name of the roast")
    profile: str = Field(..., description="Roast profile used")
    notes: str = Field(default="", description="Notes about this roast")
    data: List[Dict[str, float]] = Field(..., description="Temperature data points")