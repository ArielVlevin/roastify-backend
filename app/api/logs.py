"""
API routes for logs and data storage.
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional

from app.models import RoastLog, SaveRoastRequest,MessageResponse
from app.core import storage, monitor
from app.config import logger

router = APIRouter(prefix="/api", tags=["logs"])

@router.post("/save", response_model=MessageResponse)
async def save_roast_data(request: SaveRoastRequest):
    """Save the current roast data to a file."""
    roast_data = monitor.get_roast_data()
    
    if len(roast_data) == 0:
        raise HTTPException(status_code=400, detail="No roast data to save")
    
    filename = storage.save_roast_data(roast_data, request)
    
    if not filename:
        raise HTTPException(status_code=500, detail="Failed to save roast data")
    
    return {"message": f"Roast data saved to {filename}"}

@router.get("/logs", response_model=List[RoastLog])
async def get_roast_logs():
    """Get a list of all saved roast logs."""
    logs = storage.get_roast_logs()
    return logs

@router.get("/logs/{log_id}", response_model=RoastLog)
async def get_roast_log(log_id: str = Path(..., description="Log ID")):
    """Get a specific roast log by ID."""
    log = storage.get_roast_log(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail=f"Log file {log_id} not found")
    
    return log

@router.delete("/logs/{log_id}", response_model=MessageResponse)
async def delete_roast_log(log_id: str = Path(..., description="Log ID")):
    """Delete a specific roast log."""
    success = storage.delete_roast_log(log_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Failed to delete log file {log_id}")
    
    return {"message": f"Log file {log_id} deleted successfully"}