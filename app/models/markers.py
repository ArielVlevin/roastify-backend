"""
Pydantic data models for roast markers.
"""
from typing import Optional
from pydantic import BaseModel, Field

class RoastMarker(BaseModel):
    """Represents a marker in the roast process."""
    id: str = Field(..., description="Unique identifier for the marker")
    time: float = Field(..., description="Time in seconds from start of roast")
    temperature: float = Field(..., description="Temperature in Celsius at marker time")
    label: str = Field(..., description="Label text for the marker")
    color: Optional[str] = Field("#333333", description="Color for the marker (HEX)")
    notes: Optional[str] = Field("", description="Additional notes about the marker")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "marker-12345",
                "time": 360.0,
                "temperature": 190.5,
                "label": "First Crack",
                "color": "#FF5733",
                "notes": "First crack detected"
            }
        }