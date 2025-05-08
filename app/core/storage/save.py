"""
Functions for saving roast data.
"""
import os
import json
import time
from typing import List, Dict, Any, Optional

from app.config import settings, logger
from app.core.models.roast_log import RoastLog, SaveRoastRequest, RoastSaveData
from app.core.storage.base import ensure_logs_directory, get_full_filepath
from app.core.storage.id import generate_id
from app.core.models.crack import CrackStatus
from app.core.models.markers import Marker
from app.core.models.temp import TemperaturePoint
from app.core import monitor

def save_roast_data(
    roast_data: List[TemperaturePoint], 
    request: SaveRoastRequest,
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
    
    id = generate_id()
    filename =  f"roast_{id}.json"
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    marks = request.markers
    serialized_markers = [marker.model_dump() for marker in marks]
    
    # Create the save data structure
    save_data : RoastLog = {
        "id": id,
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "name": request.name,
        "profile": request.profile,
        "notes": request.notes or "",
        "data": roast_data,
        "markers": serialized_markers or [],
        "crack_status": request.crack_data or {}
    }
    try:
        # Ensure directory exists
        ensure_logs_directory()
        
        filepath = get_full_filepath(filename)
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
        
        logger.info(f"Roast data saved to {filename}")
        return id
    except Exception as e:
        logger.error(f"Error saving roast data: {str(e)}")
        return None