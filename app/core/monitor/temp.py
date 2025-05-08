"""
Temperature monitoring functions for the Coffee Roaster API.
Core temperature functionality and monitoring thread.
"""
import time
import threading
import copy
from typing import List, Dict, Optional

from app.config import settings, logger
from app.core import simulator, hardware
from app.core.monitor import state,crack
from app.core.models.temp import TemperaturePoint

def get_current_temperature() -> float:
    """
    Get the current temperature from hardware or simulator.
    
    Returns:
        float: Current temperature in Celsius
    """
    if settings.SIMULATION_MODE:
        return simulator.get_simulated_temperature()
    else:
        # Implement hardware.get_current_temperature() as needed
        try:
            hw_temp = hardware.get_current_temperature()
            if hw_temp is not None:
                return hw_temp
        except:
            pass
        # Fall back to simulator if hardware reading failed
        return simulator.get_simulated_temperature()

def _temperature_monitoring_task() -> None:
    """Background task for temperature monitoring."""
    logger.info(f"{'Simulation' if settings.SIMULATION_MODE else 'Temperature'} monitoring started")
    
    last_log_time = 0
    
    while not state.stop_monitor:
        try:
            if state.is_roasting:
                # Get current temperature (updates simulator if in simulation mode)
                if settings.SIMULATION_MODE:
                    current_temp = simulator.update_temperature()
                else:
                    current_temp = get_current_temperature()
                    
                # Calculate elapsed time in seconds
                elapsed_time = (time.time() - state.roast_start_time)  # seconds
                
                # Record the data point
                data_point = {
                    "time": round(elapsed_time, 1),
                    "temperature": round(current_temp, 1)  # Consistent decimal precision
                }
                state.roast_data.append(data_point)
                
                # Call temperature change callback if registered
                if state.on_temperature_change:
                    state.on_temperature_change(current_temp)
                
                # Check for cracks
                crack.check_for_cracks(current_temp, elapsed_time)
                
                # Log temperature every 60 seconds
                current_time = int(elapsed_time)
                if current_time >= last_log_time + 60:
                    logger.debug(f"Temperature: {current_temp:.1f}°C, Time: {elapsed_time:.1f} sec")
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
    if state.monitor_thread is not None and state.monitor_thread.is_alive():
        logger.debug("Monitoring thread already running")
        return True
    
    state.stop_monitor = False
    
    # Start monitoring thread
    state.monitor_thread = threading.Thread(target=_temperature_monitoring_task)
    state.monitor_thread.daemon = True  # Thread will exit when main program exits
    state.monitor_thread.start()
    
    return True

def stop_monitoring() -> None:
    """Stop the temperature monitoring thread."""
    if state.monitor_thread is None or not state.monitor_thread.is_alive():
        logger.debug("No monitoring thread running")
        return
    
    logger.info("Stopping temperature monitoring")
    state.stop_monitor = True
    
    # Wait for thread to finish
    state.monitor_thread.join(timeout=2.0)
    logger.info("Temperature monitoring stopped")


def get_roast_data() -> List[TemperaturePoint]:
    """
    Get the current roast data points.
    
    Returns:
        list: List of temperature data points
    """
    # Return a copy to prevent external modification
    return copy.deepcopy(state.roast_data)





def restore_data(data_points):
    """
    Restore temperature data from client.
    Used when syncing state between client and server.
    
    Args:
        data_points: List of temperature data points to restore
    """
    if not data_points:
        return
    
    # Copy data to prevent reference issues
    state.roast_data = copy.deepcopy(data_points)
    
    # If we have data, update the current temperature
    if len(state.roast_data) > 0:
        last_point = state.roast_data[-1]
        # Update simulator temperature to match
        simulator.current_temperature = last_point["temperature"]
        
    logger.info(f"Restored {len(data_points)} data points from client")