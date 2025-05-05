"""
API routes for the roasting process.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from app.models.schemas import (
    TemperatureResponse,
    StatusResponse,
    HeatLevelRequest,
    RoastStartResponse,
    MessageResponse
)
from app.services import monitoring
from app.core import simulator
from app.config import logger

router = APIRouter(prefix="/api", tags=["roast"])


@router.get("/temperature", response_model=TemperatureResponse)
async def get_temperature():
    """Get the current temperature."""
    temperature = monitoring.get_current_temperature()
    return {
        "temperature": round(temperature, 1),
        "timestamp": monitoring.time.time()
    }

@router.get("/data", response_model=List[Dict[str, float]])
async def get_roast_data():
    """Get all roast data points."""
    return monitoring.get_roast_data()

@router.post("/start", response_model=RoastStartResponse)
async def start_roast(background_tasks: BackgroundTasks):
    """Start the roasting process."""
    if monitoring.is_roasting:
        raise HTTPException(status_code=400, detail="Roast already in progress")
    
    # Start the roast
    start_time = monitoring.start_roast()
    
    # Ensure monitoring is running
    monitoring.start_monitoring()
    
    return {
        "message": "Roast process started",
        "time": start_time
    }

@router.post("/pause", response_model=MessageResponse)
async def pause_roast():
    """Pause the roasting process."""
    if not monitoring.is_roasting:
        raise HTTPException(status_code=400, detail="No roast in progress")
    
    monitoring.pause_roast()
    return {"message": "Roast process paused"}

@router.post("/reset", response_model=MessageResponse)
async def reset_roast():
    """Reset the roasting process."""
    monitoring.reset_roast()
    return {"message": "Roast process reset"}

@router.post("/heat", response_model=MessageResponse)
async def set_heat_level(request: HeatLevelRequest):
    """Set the heat level."""
    success = monitoring.set_heat_level(request.level)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to set heat level")
    
    return {"message": f"Heat level set to {request.level}"}

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get the current status of the roaster."""
    status = monitoring.get_status()
    return status

@router.get("/roast-stage", response_model=str)
async def get_roast_stage():
    """Get the current roast stage description."""
    stage = monitoring.get_roast_stage()
    return stage

@router.get("/crack-status", response_model=Dict[str, bool])
async def get_crack_status():
    """Get the status of first and second crack detection."""
    status = monitoring.get_crack_status()
    return status


class SyncStateRequest(BaseModel):
    """Request model for syncing state."""
    is_roasting: bool
    data: List[Dict[str, float]] = []
    start_time: float = 0
    crack_status: Optional[Dict[str, bool]] = None

class SyncStateResponse(BaseModel):
    """Response model for sync state."""
    is_roasting: bool
    temperature: float
    heat_level: int
    elapsed_time: float
    start_time: float
    data_points: List[Dict[str, float]]
    crack_status: Dict[str, bool]
    message: str = "State synchronized successfully"

@router.post("/sync-state", response_model=SyncStateResponse)
async def sync_roast_state(request: SyncStateRequest):
    """
    Synchronize roast state between client and server.
    This allows the client to recover from unexpected disconnections
    and ensures consistent state between client and server.
    """
    # Get current monitoring state
    client_is_roasting = request.is_roasting
    client_data = request.data
    client_start_time = request.start_time
    client_crack_status = request.crack_status
    
    # If client has valid data but server thinks we're still roasting,
    # trust the client and update server state
    if len(client_data) > 0 and monitoring.is_roasting != client_is_roasting:
        # Update server state to match client state
        if client_is_roasting:
            logger.info("Syncing: Client is roasting but server wasn't. Updating server state.")
            # Don't call start_roast as it would reset data and cause a 400 error
            monitoring.is_roasting = True
        else:
            logger.info("Syncing: Client is not roasting but server was. Pausing on server.")
            monitoring.pause_roast()
        
        # If client has data but server doesn't, restore it
        server_data = monitoring.get_roast_data()
        if len(server_data) == 0 and len(client_data) > 0:
            # This requires a new function in monitoring service
            monitoring.restore_data(client_data)
            
        # Update start time if needed
        if client_start_time > 0:
            monitoring.set_start_time(client_start_time)
            
        # Update crack status if provided
        if client_crack_status is not None:
            # Ensure the function exists in monitoring module
            if hasattr(monitoring, 'restore_crack_status'):
                monitoring.restore_crack_status(
                    client_crack_status.get("first", False),
                    client_crack_status.get("second", False)
                )
            else:
                logger.warning("Cannot restore crack status: function not implemented")
    
    # Get current status after sync
    status = monitoring.get_status()
    
    # Get crack status
    if hasattr(monitoring, 'get_crack_status'):
        crack_status = monitoring.get_crack_status()
    else:
        # Fallback if function doesn't exist
        crack_status = {"first": False, "second": False}
    
    # Get all data points
    data_points = monitoring.get_roast_data()
    
    # Return enhanced server state after sync
    return {
        "is_roasting": monitoring.is_roasting,
        "temperature": status["temperature"],
        "heat_level": status["heat_level"],
        "elapsed_time": status["elapsed_time"],
        "start_time": monitoring.roast_start_time,
        "data_points": data_points,
        "crack_status": crack_status,
        "message": "State synchronized successfully"
    }
    
from app.core import  simulator

    
class ForceResetResponse(BaseModel):
    status: str
    message: str

@router.post("/force-reset", response_model=ForceResetResponse)
async def force_reset_roast():
    """
    Force reset the roast process, even if one is in progress.
    This is a more aggressive reset for recovery scenarios.
    """
    try:
        # Stop monitoring if active
        monitoring.stop_monitoring()
        
        # Reset roast state
        monitoring.reset_roast()
        
        # Reset start time to 0
        monitoring.set_start_time(0)
        
        # Reset simulator to room temperature
        simulator.reset_simulator()
        simulator.current_temperature = 70.0  # Start at room temperature
        
        # Restart monitoring
        monitoring.start_monitoring()
        
        return {
            "status": "success",
            "message": "Roast forcefully reset and monitoring restarted"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to force reset roast: {str(e)}"
        )