"""
Pydantic data models for API responses.
"""
from typing import List, Optional, Any
from pydantic import BaseModel, Field

class TemperatureResponse(BaseModel):
    """Response model for temperature endpoint."""
    temperature: float = Field(..., description="Current temperature in Celsius")
    timestamp: float = Field(..., description="Unix timestamp of the reading")
    
    class Config:
        schema_extra = {
            "example": {
                "temperature": 190.5,
                "timestamp": 1619712000
            }
        }

class StatusResponse(BaseModel):
    """Response model for roaster status."""
    is_roasting: bool = Field(..., description="Whether roasting is currently active")
    temperature: float = Field(..., description="Current temperature in Celsius")
    elapsed_time: float = Field(..., description="Elapsed time in seconds")
    roast_stage: str = Field(..., description="Current roast stage")
    crack_status: dict = Field(..., description="Crack detection status")
    
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

class MessageResponse(BaseModel):
    """Generic response with a message."""
    message: str = Field(..., description="Response message")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Roast started successfully"
            }
        }

class RoastStartResponse(BaseModel):
    """Response model for starting a roast."""
    message: str = Field(..., description="Status message")
    time: float = Field(..., description="Start time as Unix timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Roast started successfully",
                "time": 1619712000
            }
        }