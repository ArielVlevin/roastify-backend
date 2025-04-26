"""
Hardware interface for the Coffee Roaster API.
Manages communication with Phidget devices.
"""
import logging
from typing import Callable, Optional

from app.config import settings, logger

# Global variables for hardware devices
temp_sensor = None
heater_control = None

def init_hardware() -> bool:
    """
    Initialize and connect to Phidget hardware devices.
    
    Returns:
        bool: True if successful, False otherwise
    """
    if settings.SIMULATION_MODE:
        logger.info("Simulation mode enabled, skipping Phidget setup")
        return True
        
    global temp_sensor, heater_control
    
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
        logger.info(f"Temperature sensor attached: {temp_sensor.getDeviceName()}")
        
        # Setup digital output for heater control
        heater_control = DigitalOutput()
        heater_control.setDeviceSerialNumber(settings.PHIDGET_SERIAL_NUMBER)
        heater_control.setHubPort(settings.HEATER_PORT)
        heater_control.setChannel(settings.HEATER_CHANNEL)
        
        # Open heater control and wait for attachment
        heater_control.openWaitForAttachment(5000)
        logger.info(f"Heater control attached: {heater_control.getDeviceName()}")
        
        return True
    
    except Exception as e:
        logger.error(f"Phidget Exception: {str(e)}")
        logger.warning("Hardware initialization failed")
        return False

def set_temperature_change_handler(callback: Callable[[float], None]) -> bool:
    """
    Set a callback function to be called when the temperature changes.
    
    Args:
        callback: Function that takes the temperature value as an argument
        
    Returns:
        bool: True if successful, False otherwise
    """
    if settings.SIMULATION_MODE or not temp_sensor:
        logger.debug("Cannot set temperature handler in simulation mode or if sensor not initialized")
        return False
        
    try:
        def handler_wrapper(self, temperature: float):
            # Convert to Fahrenheit if your sensor returns Celsius
            temp_fahrenheit = temperature * 9/5 + 32
            callback(temp_fahrenheit)
            
        temp_sensor.setOnTemperatureChangeHandler(handler_wrapper)
        return True
    except Exception as e:
        logger.error(f"Error setting temperature handler: {str(e)}")
        return False

def set_heat_level(level: int) -> bool:
    """
    Set the heat level on the physical heater control.
    
    Args:
        level: Heat level (1-10)
        
    Returns:
        bool: True if successful, False otherwise
    """
    if settings.SIMULATION_MODE:
        logger.debug(f"Simulation: Heat level set to {level}")
        return True
        
    if not heater_control:
        logger.warning("Heater control not initialized")
        return False
    
    try:
        # Convert heat level (1-10) to duty cycle (0.1-1.0)
        duty_cycle = level / settings.MAX_HEAT_LEVEL
        
        # Simple on/off control - in a real system you might use PWM
        heater_control.setState(True)
        logger.info(f"Heat level set to {level} (duty cycle: {duty_cycle:.1f})")
        return True
    except Exception as e:
        logger.error(f"Heater control error: {str(e)}")
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
        # Convert to Fahrenheit
        fahrenheit = celsius * 9/5 + 32
        return fahrenheit
    except Exception as e:
        logger.error(f"Error reading temperature: {str(e)}")
        return None

def cleanup_hardware() -> None:
    """Clean up resources when shutting down."""
    global temp_sensor, heater_control
    
    if settings.SIMULATION_MODE:
        return
        
    logger.info("Cleaning up hardware resources...")
    
    try:
        if temp_sensor:
            temp_sensor.close()
            temp_sensor = None
            
        if heater_control:
            heater_control.setState(False)  # Turn off heater
            heater_control.close()
            heater_control = None
            
        logger.info("Hardware cleanup complete")
    except Exception as e:
        logger.error(f"Error during hardware cleanup: {str(e)}")