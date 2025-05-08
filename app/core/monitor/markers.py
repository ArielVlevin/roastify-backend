"""
Marker management functionality for the Coffee Roaster API.
"""
import copy
import uuid
from typing import List, Dict, Any, Optional
from app.config import logger
from app.core.monitor import state
from app.core.models.markers import Marker

def create_marker(time_value: float, temperature: float, label: str, 
                 color: str = "#333333", notes: str = "") -> Dict[str, Any]:
    """
    Create a new roast marker.
    
    Args:
        time_value: Time in seconds from the start of roast
        temperature: Temperature in Celsius
        label: Label text for the marker
        color: Color for marker (default: "#333333")
        notes: Additional notes (optional)
        
    Returns:
        dict: Marker data
    """
    return {
        "id": str(uuid.uuid4()),
        "time": time_value,
        "temperature": temperature,
        "label": label,
        "color": color,
        "notes": notes
    }

def add_marker(time_value: float, temperature: float, label: str, 
              color: str = "#333333", notes: str = "") -> Dict[str, Any]:
    """
    Add a marker to the current roast.
    
    Args:
        time_value: Time in seconds from the start of roast
        temperature: Temperature in Celsius
        label: Label text for the marker
        color: Color for marker (default: "#333333")
        notes: Additional notes (optional)
        
    Returns:
        dict: Created marker
    """
    marker = create_marker(time_value, temperature, label, color, notes)
    state.markers.append(marker)
    logger.info(f"Added marker '{label}' at {time_value}s / {temperature}°C")
    
    return marker

def remove_marker(marker_id: str) -> bool:
    """
    Remove a marker by ID.
    
    Args:
        marker_id: ID of the marker to remove
        
    Returns:
        bool: True if marker was found and removed
    """
    original_count = len(state.markers)
    state.markers = [m for m in state.markers if m["id"] != marker_id]
    
    was_removed = len(state.markers) < original_count
    if was_removed:
        logger.info(f"Removed marker with ID {marker_id}")
    
    return was_removed

def get_markers() -> List[Marker]:
    """
    Get all markers for the current roast.
    
    Returns:
        list: List of marker dictionaries
    """
    return copy.deepcopy(state.markers)

def clear_markers() -> None:
    """Clear all markers."""
    state.markers = []
    logger.info("All markers cleared")

def restore_markers(markers_data: List[Dict[str, Any]]) -> None:
    """
    Restore markers from client or saved data.
    
    Args:
        markers_data: List of marker dictionaries to restore
    """
    if markers_data:
        state.markers = copy.deepcopy(markers_data)
        logger.info(f"Restored {len(markers_data)} markers")