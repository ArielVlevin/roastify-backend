"""
Pydantic data models for temperature and roast data.
"""
from typing import Optional, List
from pydantic import BaseModel, Field

class TemperaturePoint(BaseModel):
    """Represents a single temperature data point."""
    time: float = Field(..., description="Time in seconds from start of roast")
    temperature: float = Field(..., description="Temperature in Celsius")
    