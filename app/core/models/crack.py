# app/core/models/crack.py
"""
Pydantic data models for crack detection.
"""
from typing import Optional
from pydantic import BaseModel, Field

class CrackStatus(BaseModel):
    """Status of first and second crack detection."""
    first: bool = Field(False, description="Whether first crack has been detected")
    second: bool = Field(False, description="Whether second crack has been detected")
    first_time: Optional[float] = Field(None, description="Time of first crack in seconds")
    second_time: Optional[float] = Field(None, description="Time of second crack in seconds")
    