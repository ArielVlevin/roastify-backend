"""
API routes for logs and data storage.
"""
from fastapi import APIRouter, HTTPException, Path
from typing import List, Optional

from app.core.models import RoastLog, SaveRoastRequest,MessageResponse
from app.core import storage, monitor
from app.config import logger

router = APIRouter( tags=["logs"])



@router.get("/logs")
async def get_roast_logs():
    """Get a list of all saved roast logs."""
    logs = storage.get_roast_logs()
    print("logs: ", logs)
    return logs

@router.get("/logs/{log_id}")
async def get_roast_log(log_id: str = Path(..., description="Log ID")):
    """Get a specific roast log by ID."""
    log = storage.get_roast_log(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail=f"Log file {log_id} not found")
    
    return log

@router.delete("/logs/{log_id}")
async def delete_roast_log(log_id: str = Path(..., description="Log ID")):
    """Delete a specific roast log."""
    success = storage.delete_roast_log(log_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Failed to delete log file {log_id}")
    
    return {"message": f"Log file {log_id} deleted successfully"}