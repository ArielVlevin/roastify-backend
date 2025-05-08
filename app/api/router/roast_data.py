"""
API routes for accessing roast data and temperature.
"""
from fastapi import APIRouter
from typing import List, Dict
import time

from app.core.models.responses import TemperatureResponse
from app.core import monitor
from app.core.models.temp import TemperaturePoint

router = APIRouter(tags=["roast_data"])

@router.get("/temperature")
async def get_temperature_endpoint():
    """Get the current temperature."""
    temperature = monitor.get_current_temperature()
    return {
        "temperature": round(temperature, 2),
        "time": time.time()
    }

@router.get("/data")
async def get_roast_data_endpoint():
    """Get all roast data points."""
    return monitor.get_roast_data()



@router.get("/roast-stage", response_model=str)
async def get_roast_stage_endpoint():
    """Get the current roast stage description."""
    stage = monitor.get_roast_stage()
    return stage



@router.get("/crack-status")
async def get_crack_status_endpoint():
    """Get the status of first and second crack detection."""
    status = monitor.get_crack_status()
    return status