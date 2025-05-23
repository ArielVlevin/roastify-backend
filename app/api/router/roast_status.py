"""
API routes for roast status and synchronization.
"""
from fastapi import APIRouter
from typing import List, Dict, Optional, Any
from pydantic import BaseModel

from app.core.models.responses import RoastStatusResponse
from app.core import monitor
from app.config import logger

router = APIRouter(tags=["roast_status"])

@router.get("/status")
async def get_status_endpoint():
    """Get the current status of the roaster."""
    status = monitor.get_status()
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

@router.post("/sync-state")
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