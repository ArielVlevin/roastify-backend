"""
Crack detection functionality for the Coffee Roaster API.
"""
from app.config import logger
from app.core.monitor import state
from app.core import simulator
from app.core.monitor import markers

def check_for_cracks(current_temp: float, elapsed_time: float) -> None:
    """
    Check for first and second crack detection.
    
    Args:
        current_temp: Current temperature in Celsius
        elapsed_time: Time elapsed since start of roast in seconds
    """
    # Check for first crack
    if not state.first_crack_detected and simulator.simulate_first_crack(current_temp):
        state.first_crack_detected = True
        state.first_crack_time = elapsed_time
        logger.info(f"First crack detected at {elapsed_time:.1f}s / {current_temp:.1f}°C")
        
        # Add a marker for first crack
        markers.add_marker(
            elapsed_time, 
            current_temp, 
            "First Crack", 
            "#FF5733", 
            "First crack detected"
        )
        
        if state.on_first_crack:
            state.on_first_crack()
    
    # Check for second crack
    if not state.second_crack_detected and simulator.simulate_second_crack(current_temp):
        state.second_crack_detected = True
        state.second_crack_time = elapsed_time
        logger.info(f"Second crack detected at {elapsed_time:.1f}s / {current_temp:.1f}°C")
        
        # Add a marker for second crack
        markers.add_marker(
            elapsed_time, 
            current_temp, 
            "Second Crack", 
            "#800080", 
            "Second crack detected"
        )
        
        if state.on_second_crack:
            state.on_second_crack()

def get_crack_status() -> dict:
    """
    Get the status of first and second crack with timestamps.
    
    Returns:
        dict: Status of first and second crack detection with times
    """
    return {
        "first": state.first_crack_detected,
        "second": state.second_crack_detected,
        "first_time": state.first_crack_time,
        "second_time": state.second_crack_time
    }

def restore_crack_status(first_crack: bool, second_crack: bool, 
                         first_time: float = None, second_time: float = None):
    """
    Restore crack detection status.
    Used when syncing state between client and server.
    
    Args:
        first_crack: Whether first crack has been detected
        second_crack: Whether second crack has been detected
        first_time: Time of first crack in seconds
        second_time: Time of second crack in seconds
    """
    state.first_crack_detected = first_crack
    state.second_crack_detected = second_crack
    state.first_crack_time = first_time
    state.second_crack_time = second_time
    
    logger.info(f"Restored crack status: first={first_crack}, second={second_crack}")