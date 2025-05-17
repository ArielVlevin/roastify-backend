"""
Pydantic data models for API responses.
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field

from app.core.models.status import RoastStatus
from app.core.models.temp import TemperaturePoint


class Response(BaseModel):
    """Generic response model."""
    success: bool = Field( description="Whether the response was successful")


class MessageResponse(Response):
    """Base response model."""
    message: Optional[str] = Field(..., description="Response message")


class ErrorResponse(Response):
    """Response with an error."""
    isError: bool = Field(default=True, description="Whether the response has an error")
    error: Optional[str] = Field(..., description="Error message")
    
    
class RoastStartResponse(Response):
    """Response model for starting a roast."""
    time: float = Field(..., description="Start time as Unix timestamp")
    
    
class TemperatureResponse(Response):
    """Response model for temperature endpoint."""
    point : TemperaturePoint = Field(..., description="Temperature data point")
    

class RoastStatusResponse(MessageResponse):
    """Response model for roaster status."""
    status: RoastStatus = Field(..., description="Status data")
    
    
class RoastSaveResponse(MessageResponse):
    id: str = Field(..., description="Unique identifier for the roast")
