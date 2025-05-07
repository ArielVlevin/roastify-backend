"""
Functions for saving roast data.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional

from app.config import settings, logger
from app.models.roast_log import SaveRoastRequest, RoastSaveData
from app.core.storage.base import ensure_logs_directory, get_full_filepath

def save_roast_data(
    roast_data: List[Dict[str, float]], 
    request: SaveRoastRequest,
    markers: Optional[List[Dict[str, Any]]] = None,
    crack_data: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Save roast data to a file.
    
    Args:
        roast_data: List of temperature data points
        request: Details about the roast to save
        markers: Optional list of markers
        crack_data: Optional crack detection data
        
    Returns:
        str: Filename where data was saved, or None if failed
    """
    if len(roast_data) == 0:
        logger.warning("Attempted to save empty roast data")
        return None
    
    filename = request.filename or f"roast_{int(time.time())}.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    # Create the save data structure
    save_data = {
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "name": request.name,
        "profile": request.profile,
        "notes": request.notes or "",
        "data": roast_data
    }
    
    # Add markers if available
    if markers:
        save_data["markers"] = markers
    
    # Add crack data if available
    if crack_data:
        save_data["first_crack"] = crack_data.get("first", False)
        save_data["second_crack"] = crack_data.get("second", False)
        save_data["first_crack_time"] = crack_data.get("first_time")
        save_data["second_crack_time"] = crack_data.get("second_time")
    
    try:
        # Ensure directory exists
        ensure_logs_directory()
        
        filepath = get_full_filepath(filename)
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        logger.info(f"Roast data saved to {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving roast data: {str(e)}")
        return None