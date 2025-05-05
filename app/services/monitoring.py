"""
Temperature monitoring service for the Coffee Roaster API.
Manages the monitoring thread and data collection.
"""
import time
import threading
import copy
from typing import List, Dict, Optional, Callable

from app.config import settings, logger
from app.core import hardware, simulator

# Global state
is_roasting = False
heat_level = settings.DEFAULT_HEAT_LEVEL
roast_start_time = 0
roast_data: List[Dict[str, float]] = []

# Thread for continuous monitoring
monitor_thread = None
stop_monitor = False

# Callbacks
on_temperature_change: Optional[Callable[[float], None]] = None
on_first_crack: Optional[Callable[[], None]] = None
on_second_crack: Optional[Callable[[], None]] = None

# State for crack detection
first_crack_detected = False
second_crack_detected = False

# Current roast ID for logging
current_roast_id = None

def get_current_temperature() -> float:
    """
    Get the current temperature from hardware or simulator.
    
    Returns:
        float: Current temperature in Fahrenheit
    """
    if settings.SIMULATION_MODE:
        return simulator.get_simulated_temperature()
    else:
        hw_temp = hardware.get_current_temperature()
        if hw_temp is not None:
            return hw_temp
        # Fall back to simulator if hardware reading failed
        return simulator.get_simulated_temperature()

def set_heat_level(level: int) -> bool:
    """
    Set the heat level and apply to hardware if not in simulation mode.
    
    Args:
        level: Heat level (1-10)
    
    Returns:
        bool: True if successful
    """
    global heat_level
    
    # Validate the heat level
    if level < settings.MIN_HEAT_LEVEL or level > settings.MAX_HEAT_LEVEL:
        logger.warning(f"Invalid heat level: {level}")
        return False
    
    heat_level = level
    logger.info(f"Heat level set to {level}")
    
    # Apply to hardware if not in simulation mode
    if not settings.SIMULATION_MODE:
        result = hardware.set_heat_level(level)
        if not result:
            logger.error(f"Failed to set hardware heat level to {level}")
        return result
    
    return True

def start_roast() -> float:
    """
    Start the roasting process.
    
    Returns:
        float: Start time as Unix timestamp
    """
    global is_roasting, roast_data, roast_start_time
    global first_crack_detected, second_crack_detected
    global current_roast_id
    
    # Reset state
    is_roasting = True
    roast_data = []
    roast_start_time = time.time()
    first_crack_detected = False
    second_crack_detected = False
    
    # Create new roast logger if needed
    if hasattr(logger, 'create_roast_logger'):
        current_roast_id = logger.create_roast_logger()
    
    logger.info("Roast process started")
    return roast_start_time

def pause_roast() -> None:
    """Pause the roasting process."""
    global is_roasting
    
    is_roasting = False
    logger.info("Roast process paused")

def reset_roast() -> None:
    """Reset the roasting process to initial state."""
    global is_roasting, roast_data, first_crack_detected, second_crack_detected
    
    is_roasting = False
    roast_data = []
    first_crack_detected = False
    second_crack_detected = False
    
    # Reset simulator to room temperature
    simulator.reset_simulator()
    
    logger.info("Roast process reset")

def get_status() -> Dict[str, float]:
    """
    Get the current status of the roaster.
    
    Returns:
        dict: Status information including temperature, elapsed time, etc.
    """
    current_temp = get_current_temperature()
    
    return {
        "is_roasting": is_roasting,
        "heat_level": heat_level,
        "temperature": round(current_temp, 1),
        "elapsed_time": (time.time() - roast_start_time) if is_roasting else 0  # seconds
    }

def get_roast_data() -> List[Dict[str, float]]:
    """
    Get the current roast data points.
    
    Returns:
        list: List of temperature data points
    """
    # Return a copy to prevent external modification
    return copy.deepcopy(roast_data)

def _temperature_monitoring_task() -> None:
    """Background task for temperature monitoring."""
    global is_roasting, roast_data, first_crack_detected, second_crack_detected, stop_monitor
    
    logger.info(f"{'Simulation' if settings.SIMULATION_MODE else 'Temperature'} monitoring started")
    
    last_log_time = 0
    
    while not stop_monitor:
        try:
            if is_roasting:
                # Get current temperature (updates simulator if in simulation mode)
                if settings.SIMULATION_MODE:
                    current_temp = simulator.update_temperature(heat_level)
                else:
                    current_temp = get_current_temperature()
                    
                # Calculate elapsed time in seconds
                elapsed_time = (time.time() - roast_start_time)  # seconds
                
                # Record the data point
                data_point = {
                    "time": round(elapsed_time, 1),
                    "temperature": round(current_temp, 1)  # Consistent decimal precision
                }
                roast_data.append(data_point)
                
                # Call temperature change callback if registered
                if on_temperature_change:
                    on_temperature_change(current_temp)
                
                # Check for first crack
                if not first_crack_detected and simulator.simulate_first_crack(current_temp):
                    first_crack_detected = True
                    logger.info("First crack detected")
                    if on_first_crack:
                        on_first_crack()
                
                # Check for second crack
                if not second_crack_detected and simulator.simulate_second_crack(current_temp):
                    second_crack_detected = True
                    logger.info("Second crack detected")
                    if on_second_crack:
                        on_second_crack()
                
                # Log temperature every 60 seconds
                current_time = int(elapsed_time)
                if current_time >= last_log_time + 60:
                    logger.debug(f"Temperature: {current_temp:.1f}°F, Time: {elapsed_time:.1f} sec")
                    last_log_time = current_time
            
            # Sleep for a short interval
            time.sleep(settings.TEMPERATURE_UPDATE_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in temperature monitoring: {str(e)}")
            time.sleep(1)  # Wait a bit longer on error

def start_monitoring() -> bool:
    """
    Start the temperature monitoring thread.
    
    Returns:
        bool: True if started successfully
    """
    global monitor_thread, stop_monitor
    
    if monitor_thread is not None and monitor_thread.is_alive():
        logger.debug("Monitoring thread already running")
        return True
    
    stop_monitor = False
    
    # Start monitoring thread
    monitor_thread = threading.Thread(target=_temperature_monitoring_task)
    monitor_thread.daemon = True  # Thread will exit when main program exits
    monitor_thread.start()
    
    return True

def stop_monitoring() -> None:
    """Stop the temperature monitoring thread."""
    global stop_monitor
    
    if monitor_thread is None or not monitor_thread.is_alive():
        logger.debug("No monitoring thread running")
        return
    
    logger.info("Stopping temperature monitoring")
    stop_monitor = True
    
    # Wait for thread to finish
    monitor_thread.join(timeout=2.0)
    logger.info("Temperature monitoring stopped")

def register_temperature_callback(callback: Callable[[float], None]) -> None:
    """Register a callback for temperature changes."""
    global on_temperature_change
    on_temperature_change = callback

def register_first_crack_callback(callback: Callable[[], None]) -> None:
    """Register a callback for first crack detection."""
    global on_first_crack
    on_first_crack = callback

def register_second_crack_callback(callback: Callable[[], None]) -> None:
    """Register a callback for second crack detection."""
    global on_second_crack
    on_second_crack = callback

def get_crack_status() -> Dict[str, bool]:
    """
    Get the status of first and second crack.
    
    Returns:
        dict: Status of first and second crack detection
    """
    return {
        "first": first_crack_detected,
        "second": second_crack_detected
    }

def get_roast_stage() -> str:
    """
    Get the current roast stage description.
    
    Returns:
        str: Description of current roast stage
    """
    current_temp = get_current_temperature()
    return simulator.get_roast_stage(current_temp)

def restore_data(data_points):
    """
    Restore temperature data from client.
    Used when syncing state between client and server.
    
    Args:
        data_points: List of temperature data points to restore
    """
    global roast_data
    
    if not data_points:
        return
    
    # Copy data to prevent reference issues
    roast_data = copy.deepcopy(data_points)
    
    # If we have data, update the current temperature
    if len(roast_data) > 0:
        last_point = roast_data[-1]
        # Update simulator temperature to match
        simulator.current_temperature = last_point["temperature"]
        
    logger.info(f"Restored {len(data_points)} data points from client")

def set_start_time(start_time):
    """
    Set the roast start time.
    Used when syncing state between client and server.
    
    Args:
        start_time: Unix timestamp for roast start
    """
    global roast_start_time
    
    if start_time > 0:
        roast_start_time = start_time
        logger.info(f"Set roast start time to {start_time}")

def force_start_roast():
    """
    Force start a roast even if one is already in progress.
    Used in recovery scenarios.
    
    Returns:
        float: Start time as Unix timestamp
    """
    global is_roasting, roast_data, roast_start_time
    global first_crack_detected, second_crack_detected
    global current_roast_id
    
    # Reset state
    is_roasting = True
    roast_data = []
    roast_start_time = time.time()
    first_crack_detected = False
    second_crack_detected = False
    
    # Create new roast logger if available
    if hasattr(logger, 'create_roast_logger'):
        current_roast_id = logger.create_roast_logger()
    
    logger.info("Roast process force-started")
    return roast_start_time

def restore_crack_status(first_crack: bool, second_crack: bool):
    """
    Restore crack detection status.
    Used when syncing state between client and server.
    
    Args:
        first_crack: Whether first crack has been detected
        second_crack: Whether second crack has been detected
    """
    global first_crack_detected, second_crack_detected
    
    first_crack_detected = first_crack
    second_crack_detected = second_crack
    
    logger.info(f"Restored crack status: first={first_crack}, second={second_crack}")