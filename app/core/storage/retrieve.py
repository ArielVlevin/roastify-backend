"""
Functions for retrieving saved roast data.
"""
import os
import json
from typing import List, Dict, Any, Optional

from app.config import settings, logger
from app.models.roast_log import RoastLog
from app.core.storage.base import ensure_logs_directory, get_full_filepath

def get_roast_logs() -> List[Dict[str, Any]]:
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
                log_id = filename.replace('.json', '')
                log = get_roast_log(log_id)
                if log:
                    logs.append(log)
            except Exception as e:
                logger.error(f"Error reading {filename}: {str(e)}")
        
        # Sort logs by date (newest first)
        logs.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return logs
    except Exception as e:
        logger.error(f"Error listing roast logs: {str(e)}")
        return []

def get_roast_log(log_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific roast log by ID.
    
    Args:
        log_id: Unique identifier for the roast (filename without .json)
        
    Returns:
        dict: Roast log data if found, None otherwise
    """
    try:
        filename = f"{log_id}.json"
        filepath = get_full_filepath(filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Log file not found: {filename}")
            return None
            
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Add the ID to the data
        data["id"] = log_id
        
        # Calculate duration from the data
        if data.get("data") and len(data["data"]) > 0:
            data["duration"] = data["data"][-1]["time"]
        else:
            data["duration"] = 0
            
        return data
    except FileNotFoundError:
        logger.warning(f"Log file not found: {log_id}")
        return None
    except Exception as e:
        logger.error(f"Error reading log file {log_id}: {str(e)}")
        return None

def format_log_for_api(log_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format a raw log data structure into the API response format.
    
    Args:
        log_data: Raw log data from the file
        
    Returns:
        dict: Formatted log data for API response
    """
    # Extract the temperature data points
    temp_data = log_data.get("data", [])
    
    # Extract markers if available
    markers = log_data.get("markers", [])
    
    # Format the response
    formatted_data = {
        "id": log_data.get("id"),
        "name": log_data.get("name", "Unnamed Roast"),
        "date": log_data.get("date", ""),
        "profile": log_data.get("profile", "Custom"),
        "duration": log_data.get("duration", 0),
        "temperature_data": temp_data,
        "markers": markers,
        "notes": log_data.get("notes", ""),
        "first_crack_time": log_data.get("first_crack_time"),
        "second_crack_time": log_data.get("second_crack_time")
    }
            
    return formatted_data