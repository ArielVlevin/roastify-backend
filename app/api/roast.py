"""
API routes for the roasting process.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from app.models.responses import (
    TemperatureResponse,
    StatusResponse,
    RoastStartResponse,
    MessageResponse
)

from app.core import monitor

from app.core import simulator, monitor
from app.config import logger

router = APIRouter(prefix="/api", tags=["roast"])


@router.get("/temperature", response_model=TemperatureResponse)
async def get_temperature_endpoint():
    """Get the current temperature."""
    temperature = monitor.get_current_temperature()
    import time  # Importamos time aquí ya que no usamos el tiempo del módulo monitoring
    return {
        "temperature": round(temperature, 1),
        "timestamp": time.time()
    }

@router.get("/data", response_model=List[Dict[str, float]])
async def get_roast_data_endpoint():
    """Get all roast data points."""
    return monitor.get_roast_data()

@router.post("/start", response_model=RoastStartResponse)
async def start_roast_endpoint(background_tasks: BackgroundTasks):
    """Start the roasting process."""
    if monitor.is_roasting:
        raise HTTPException(status_code=400, detail="Roast already in progress")
    
    # Start the roast
    start_time = monitor.start_roast()
    
    # Ensure monitoring is running
    monitor.start_monitoring()
    
    return {
        "message": "Roast process started",
        "time": start_time
    }

@router.post("/pause", response_model=MessageResponse)
async def pause_roast_endpoint():
    """Pause the roasting process."""
    if not monitor.state.is_roasting:
        raise HTTPException(status_code=400, detail="No roast in progress")
    
    monitor.pause_roast()
    return {"message": "Roast process paused"}

@router.post("/reset", response_model=MessageResponse)
async def reset_roast_endpoint():
    """Reset the roasting process."""
    monitor.reset_roast()
    return {"message": "Roast process reset"}

@router.get("/status", response_model=StatusResponse)
async def get_status_endpoint():
    """Get the current status of the roaster."""
    status = monitor.get_status()
    return status

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


class SyncStateRequest(BaseModel):
    """Request model for syncing state."""
    is_roasting: bool
    data: List[Dict[str, float]] = []
    start_time: float = 0
    crack_status: Optional[Dict[str, bool]] = None
    markers: Optional[List[Dict[str, Any]]] = None

class SyncStateResponse(BaseModel):
    """Response model for sync state."""
    is_roasting: bool
    temperature: float
    elapsed_time: float
    start_time: float
    data_points: List[Dict[str, float]]
    crack_status: Dict[str, Any]
    markers: List[Dict[str, Any]] = []
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
    client_markers = request.markers
    
    # If client has valid data but server thinks we're still roasting,
    # trust the client and update server state
    if len(client_data) > 0 and monitor.is_roasting != client_is_roasting:
        # Update server state to match client state
        if client_is_roasting:
            logger.info("Syncing: Client is roasting but server wasn't. Updating server state.")
            # Don't call start_roast as it would reset data and cause a 400 error
            from app.core.monitor.state import is_roasting as is_roasting_state
            is_roasting_state = True
        else:
            logger.info("Syncing: Client is not roasting but server was. Pausing on server.")
            monitor.pause_roast()
        
        # If client has data but server doesn't, restore it
        server_data = monitor.get_roast_data()
        if len(server_data) == 0 and len(client_data) > 0:
            monitor.restore_data(client_data)
            
        # Update start time if needed
        if client_start_time > 0:
            monitor.set_start_time(client_start_time)
            
        # Update crack status if provided
        if client_crack_status is not None:
            monitor.restore_crack_status(
                client_crack_status.get("first", False),
                client_crack_status.get("second", False),
                client_crack_status.get("first_time"),
                client_crack_status.get("second_time")
            )
            
        # Update markers if provided
        if client_markers:
            monitor.restore_markers(client_markers)
    
    # Get current status after sync
    status = monitor.get_status()
    
    # Get crack status
    crack_status = monitor.get_crack_status()
    
    # Get all data points
    data_points = monitor.get_roast_data()
    
    # Get all markers
    all_markers = monitor.get_markers()
    
    # Return enhanced server state after sync
    return {
        "is_roasting": monitor.is_roasting,
        "temperature": status["temperature"],
        "elapsed_time": status["elapsed_time"],
        "start_time": monitor.roast_start_time,
        "data_points": data_points,
        "crack_status": crack_status,
        "markers": all_markers,
        "message": "State synchronized successfully"
    }
    
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
        monitor.stop_monitoring()
        
        # Reset roast state
        monitor.reset_roast()
        
        # Reset start time to 0
        monitor.set_start_time(0)
        
        # Reset simulator to room temperature
        simulator.reset_simulator()
        simulator.current_temperature = 24.0  # Start at room temperature (Celsius)
        
        # Restart monitoring
        monitor.start_monitoring()
        
        return {
            "status": "success",
            "message": "Roast forcefully reset and monitoring restarted"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to force reset roast: {str(e)}"
        )