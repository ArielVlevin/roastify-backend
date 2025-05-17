""" 
Pydantic data models for roast markers. 
"""
from typing import Optional
from pydantic import BaseModel, Field

class Marker(BaseModel):
    """
    Represents a marker in the roast process.
    """
    id: str = Field(..., description="Unique identifier for the marker")
    time: float = Field(..., description="Time in seconds from start of roast")
    temperature: float = Field(..., description="Temperature in Celsius at marker time")
    label: str = Field(..., description="Label text for the marker")
    color: Optional[str] = Field("#333333", description="Color for the marker (HEX)")
    icon: Optional[str] = Field("", description="Icon for the marker")
    notes: Optional[str] = Field("", description="Additional notes about the marker")
    
    def to_dict(self):
        """Convert marker to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "time": self.time,
            "temperature": self.temperature,
            "label": self.label,
            "color": self.color,
            "icon": self.icon,
            "notes": self.notes
        }
        
        

    @classmethod
    def create(cls, id, time, temperature, label, color=None, notes=None):
        """Factory method to create a marker with default values."""
        return cls(
            id=id,
            time=time,
            temperature=temperature,
            label=label,
            color=color or "#333333",
            icon="",
            notes=notes or ""
        )