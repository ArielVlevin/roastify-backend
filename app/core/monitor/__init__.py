"""
Temperature monitoring service for the Coffee Roaster API.
Manages the monitoring thread and data collection with support for markers.
"""
import time
from typing import List, Dict, Any, Optional, Callable, Union

from app.config import settings, logger
from app.core import simulator
from app.core.monitor.state import *

from app.core.monitor.markers import *
# Export main functions and interfaces
from app.core.monitor.temp import  *
from app.core.monitor.crack import  *



def get_status() -> Dict[str, Any]:
    """
    Get the current status of the roaster.
    
    Returns:
        dict: Status information including temperature, elapsed time, etc.
    """
    current_temp = get_current_temperature()
    
    return {
        "is_roasting": state.is_roasting,
        "temperature": round(current_temp, 1),
        "elapsed_time": (time.time() - state.roast_start_time) if state.is_roasting else 0,
        "roast_stage": get_roast_stage(),
        "crack_status": get_crack_status()
    }

def get_roast_stage() -> str:
    """
    Get the current roast stage description.
    
    Returns:
        str: Description of current roast stage
    """
    current_temp = get_current_temperature()
    return simulator.get_roast_stage(current_temp)

def start_roast() -> float:
    """
    Start the roasting process.
    
    Returns:
        float: Start time as Unix timestamp
    """
    # Reset state
    state.is_roasting = True
    state.roast_data = []
    state.markers = []
    state.roast_start_time = time.time()
    state.first_crack_detected = False
    state.second_crack_detected = False
    state.first_crack_time = None
    state.second_crack_time = None
    
    # Create new roast logger if needed
    if hasattr(logger, 'create_roast_logger'):
        state.current_roast_id = logger.create_roast_logger()
    
    logger.info("Roast process started")
    return state.roast_start_time

def pause_roast() -> None:
    """Pause the roasting process."""
    state.is_roasting = False
    logger.info("Roast process paused")

def reset_roast() -> None:
    """Reset the roasting process to initial state."""
    state.is_roasting = False
    state.roast_data = []
    state.markers = []
    state.first_crack_detected = False
    state.second_crack_detected = False
    state.first_crack_time = None
    state.second_crack_time = None
    
    # Reset simulator to room temperature
    simulator.reset_simulator()
    
    logger.info("Roast process reset")

def set_start_time(start_time: float) -> None:
    """
    Set the roast start time.
    Used when syncing state between client and server.
    
    Args:
        start_time: Unix timestamp for roast start
    """
    if start_time > 0:
        state.roast_start_time = start_time
        logger.info(f"Set roast start time to {start_time}")

def force_start_roast() -> float:
    """
    Force start a roast even if one is already in progress.
    Used in recovery scenarios.
    
    Returns:
        float: Start time as Unix timestamp
    """
    # Reset state
    state.is_roasting = True
    state.roast_data = []
    state.roast_start_time = time.time()
    state.first_crack_detected = False
    state.second_crack_detected = False
    
    # Create new roast logger if available
    if hasattr(logger, 'create_roast_logger'):
        state.current_roast_id = logger.create_roast_logger()
    
    logger.info("Roast process force-started")
    return state.roast_start_time

def register_temperature_callback(callback: Callable[[float], None]) -> None:
    """Register a callback for temperature changes."""
    state.on_temperature_change = callback

def register_first_crack_callback(callback: Callable[[], None]) -> None:
    """Register a callback for first crack detection."""
    state.on_first_crack = callback

def register_second_crack_callback(callback: Callable[[], None]) -> None:
    """Register a callback for second crack detection."""
    state.on_second_crack = callback

def prepare_roast_save_data(name: str, profile: str, notes: str = "") -> Dict[str, Any]:
    """
    Prepare data for saving a roast log.
    
    Args:
        name: Name of the roast
        profile: Profile used
        notes: Additional notes
        
    Returns:
        dict: Complete roast data with temperature and markers
    """
    # Calculate duration in minutes
    duration = 0
    if len(state.roast_data) > 0:
        duration = state.roast_data[-1]["time"]  # in seconds
    
    # Create a combined data structure with temperature points and markers
    temp_data_with_markers = []
    
    # Add all temperature points
    for point in state.roast_data:
        temp_point = {
            "time": point["time"],
            "temperature": point["temperature"],
            "marker": None  # Default no marker
        }
        temp_data_with_markers.append(temp_point)
    
    # Mark points that have markers
    for marker in state.markers:
        # Find the closest temperature point
        closest_idx = -1
        min_diff = float('inf')
        
        for i, point in enumerate(temp_data_with_markers):
            time_diff = abs(point["time"] - marker["time"])
            if time_diff < min_diff:
                min_diff = time_diff
                closest_idx = i
        
        if closest_idx >= 0:
            # Add marker info to the closest point
            temp_data_with_markers[closest_idx]["marker"] = marker["label"]
            temp_data_with_markers[closest_idx]["marker_id"] = marker["id"]
            temp_data_with_markers[closest_idx]["marker_color"] = marker["color"]
            temp_data_with_markers[closest_idx]["marker_notes"] = marker["notes"]
    
    # Create the save data
    save_data = {
        "timestamp": time.time(),
        "date": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        "name": name,
        "profile": profile,
        "notes": notes,
        "data": temp_data_with_markers,
        "markers": state.markers,
        "first_crack_time": state.first_crack_time,
        "second_crack_time": state.second_crack_time,
        "duration": duration,
        "roast_stage": get_roast_stage()
    }
    
    return save_data