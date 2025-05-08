"""
API routes for controlling the roasting process (start, pause, reset).
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Optional

from app.core.models.responses import (
    RoastStartResponse,
    MessageResponse
)


from app.core import monitor
from app.config import logger
from app.core import storage

router = APIRouter(tags=["roast_control"])

@router.post("/start", response_model=RoastStartResponse)
async def start_roast_endpoint(background_tasks: BackgroundTasks):
    """Start the roasting process."""
    if monitor.is_roasting:
        raise HTTPException(status_code=400, detail="Roast already in progress")
    
    # Start the roast
    start_time = monitor.start_roast()
    
    # Ensure monitoring is running
    monitor.start_monitoring()
    
    response = {
        "success": True,
        "message": "Roast process started",
        "isError": False,
        "error": None,
        "time": start_time
    }
    return response



@router.post("/pause")
async def pause_roast_endpoint():
    """Pause the roasting process."""
    if not monitor.state.is_roasting:
        raise HTTPException(status_code=400, detail="No roast in progress")
    
    monitor.pause_roast()
    return {"message": "Roast process paused", "success": True, "isError": False, "error": None}

@router.post("/reset")
async def reset_roast_endpoint():
    """Reset the roasting process."""
    monitor.reset_roast()
    return {"message": "Roast process reset", "success": True}

@router.post("/force-reset", response_model=MessageResponse)
async def force_reset_roast():
    """
    Force reset the roast process, even if one is in progress.
    This is a more aggressive reset for recovery scenarios.
    """
    try:
        # Stop monitoring if active
        monitor.stop_monitoring()
        
        # Reset roast state
        monitor.reset_roast()
        
        # Reset start time to 0
        monitor.set_start_time(0)
        
        # Reset simulator to room temperature
        from app.core import simulator
        simulator.reset_simulator()
        simulator.current_temperature = 24.0  # Start at room temperature (Celsius)
        
        # Restart monitoring
        monitor.start_monitoring()
        
        return {
            "message": "Roast forcefully reset and monitoring restarted",
            "success": True,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to force reset roast: {str(e)}"
        )
        
        
        
        
@router.post("/save")
async def save_roast_data(request: storage.SaveRoastRequest):
    """Save the current roast data to a file."""
    roast_data = monitor.get_roast_data()
    
    if len(roast_data) == 0:
        raise HTTPException(status_code=400, detail="No roast data to save")
    
    filename = storage.save_roast_data(roast_data, request)
    
    if not filename:
        raise HTTPException(status_code=500, detail="Failed to save roast data")
    
    return { "success": True, "message": f"Roast data saved to {filename}",}


