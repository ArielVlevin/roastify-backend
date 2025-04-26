"""
Storage service for the Coffee Roaster API.
Manages saving and retrieving roast logs.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional, Union

from app.config import settings, logger
from app.models.schemas import RoastLog, SaveRoastRequest, RoastSaveData

def ensure_logs_directory() -> None:
    """Ensure the logs directory exists."""
    os.makedirs(settings.LOGS_DIRECTORY, exist_ok=True)

def save_roast_data(
    roast_data: List[Dict[str, float]], 
    request: SaveRoastRequest
) -> Optional[str]:
    """
    Save roast data to a file.
    
    Args:
        roast_data: List of temperature data points
        request: Details about the roast to save
        
    Returns:
        str: Filename where data was saved, or None if failed
    """
    if len(roast_data) == 0:
        logger.warning("Attempted to save empty roast data")
        return None
    
    filename = request.filename or f"roast_{int(time.time())}.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    save_data = RoastSaveData(
        timestamp=time.time(),
        date=time.strftime("%Y-%m-%d %H:%M:%S"),
        name=request.name,
        profile=request.profile,
        notes=request.notes or "",
        data=roast_data
    )
    
    try:
        # Ensure directory exists
        ensure_logs_directory()
        
        filepath = os.path.join(settings.LOGS_DIRECTORY, filename)
        with open(filepath, 'w') as f:
            json.dump(save_data.dict(), f, indent=2)
        
        logger.info(f"Roast data saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving roast data: {str(e)}")
        return None

def get_roast_logs() -> List[RoastLog]:
    """
    Get a list of all saved roast logs.
    
    Returns:
        list: List of RoastLog objects
    """
    try:
        # Ensure directory exists
        ensure_logs_directory()
        
        # Get all .json files in the logs directory
        files = [f for f in os.listdir(settings.LOGS_DIRECTORY) if f.endswith('.json')]
        logs = []
        
        for filename in files:
            try:
                log = get_roast_log(filename.replace('.json', ''))
                if log:
                    logs.append(log)
            except Exception as e:
                logger.error(f"Error reading {filename}: {str(e)}")
        
        # Sort logs by date (newest first)
        logs.sort(key=lambda x: x.date, reverse=True)
        return logs
    except Exception as e:
        logger.error(f"Error listing roast logs: {str(e)}")
        return []

def get_roast_log(log_id: str) -> Optional[RoastLog]:
    """
    Get a specific roast log by ID.
    
    Args:
        log_id: Unique identifier for the roast (filename without .json)
        
    Returns:
        RoastLog: Roast log object if found, None otherwise
    """
    try:
        filename = f"{log_id}.json"
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(settings.LOGS_DIRECTORY, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Log file not found: {filename}")
            return None
            
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert to format expected by frontend
        response_data = RoastLog(
            id=log_id,
            name=data.get("name", "Unnamed Roast"),
            date=data.get("date", ""),
            profile=data.get("profile", "Custom"),
            duration=data["data"][-1]["time"] if data["data"] else 0,
            tempData=data["data"],
            notes=data.get("notes", ""),
            firstCrack=None,  # Can be extended later
            secondCrack=None  # Can be extended later
        )
            
        return response_data
    except FileNotFoundError:
        logger.warning(f"Log file not found: {log_id}")
        return None
    except Exception as e:
        logger.error(f"Error reading log file {log_id}: {str(e)}")
        return None

def delete_roast_log(log_id: str) -> bool:
    """
    Delete a specific roast log.
    
    Args:
        log_id: Unique identifier for the roast (filename without .json)
        
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        filename = f"{log_id}.json"
        if not filename.endswith('.json'):
            filename += '.json'
        
        filepath = os.path.join(settings.LOGS_DIRECTORY, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Log file not found for deletion: {filename}")
            return False
        
        os.remove(filepath)
        logger.info(f"Deleted log file: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error deleting log file {log_id}: {str(e)}")
        return False