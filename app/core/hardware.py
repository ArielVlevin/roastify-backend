"""
Hardware interface for the Coffee Roaster API.
Manages communication with Phidget devices.
"""
import logging
from typing import Callable, Optional

from app.config import settings, logger

# Global variables for hardware devices
temp_sensor = None

def init_hardware() -> bool:
    """
    Initialize and connect to Phidget hardware devices.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if settings.SIMULATION_MODE:
        logger.info("Simulation mode enabled, skipping Phidget setup")
        return True
        
    global temp_sensor
    
    try:
        # Import Phidget libraries inside function to avoid errors in simulation mode
        from Phidget22.Devices.TemperatureSensor import TemperatureSensor
        from Phidget22.Devices.DigitalOutput import DigitalOutput
        from Phidget22.PhidgetException import PhidgetException
        
        # Setup temperature sensor
        temp_sensor = TemperatureSensor()
        temp_sensor.setDeviceSerialNumber(settings.PHIDGET_SERIAL_NUMBER)
        temp_sensor.setHubPort(settings.HUB_PORT)
        temp_sensor.setChannel(settings.TEMP_CHANNEL)
        
       # Open temperature sensor and wait for attachment
        temp_sensor.openWaitForAttachment(5000)
        if temp_sensor.getAttached():
            logger.info(f"Temperature sensor attached: {temp_sensor.getDeviceName()}")
            return True
        else:
            logger.warning("Temperature sensor is not attached")
            return False
        
    
    except PhidgetException as e:
        logger.error(f"Phidget Error: {e.details}")
        logger.warning("Hardware initialization failed")
        return False

def get_current_temperature() -> Optional[float]:
    """
    Get the current temperature from the sensor.
    
    Returns:
        float: Current temperature in Fahrenheit or None if not available
    """
    if settings.SIMULATION_MODE or not temp_sensor:
        return None
        
    try:
        # Get temperature in Celsius
        celsius = temp_sensor.getTemperature()
        
        logger.info(f"Temperature: {celsius}°C")
        return celsius
    except Exception as e:
        logger.error(f"Error reading temperature: {str(e)}")
        return None

def cleanup_hardware() -> None:
    """Clean up resources when shutting down."""
    global temp_sensor
    
    if settings.SIMULATION_MODE:
        return
        
    logger.info("Cleaning up hardware resources...")
    
    try:
        if temp_sensor:
            temp_sensor.close()
            temp_sensor = None
            
            
        logger.info("Hardware cleanup complete")
    except Exception as e:
        logger.error(f"Error during hardware cleanup: {str(e)}")