"""
Temperature simulator for the Coffee Roaster API.
Simulates temperature changes based on heat level and time.
"""
import random
import time
from app.config import settings, logger

# Global state for simulator
current_temperature = settings.DEFAULT_TEMPERATURE
last_update_time = 0

def reset_simulator() -> None:
    """Reset simulator to initial state."""
    global current_temperature, last_update_time
    current_temperature = settings.DEFAULT_TEMPERATURE
    last_update_time = 0
    logger.debug("Simulator reset to initial state")

def get_simulated_temperature() -> float:
    """
    Get the current simulated temperature.
    
    Returns:
        float: Current temperature in Fahrenheit
    """
    global current_temperature
    return current_temperature

def update_temperature(heat_level: int, force_update: bool = False) -> float:
    """
    Update the simulated temperature based on heat level and time elapsed.
    
    Args:
        heat_level: Heat level (1-10)
        force_update: If True, update regardless of time elapsed
    
    Returns:
        float: New temperature in Fahrenheit
    """
    global current_temperature, last_update_time
    
    current_time = time.time()
    
    # Only update if enough time has passed or forced
    if not force_update and (current_time - last_update_time < settings.TEMPERATURE_UPDATE_INTERVAL):
        return current_temperature
    
    # Calculate temperature change based on heat level
    # More heat = faster temperature rise
    heat_effect = heat_level * 2
    
    # Add some randomness to make it realistic
    random_factor = random.uniform(-1, 3)
    
    # Natural cooling effect (stronger at higher temperatures)
    cooling_factor = (current_temperature - settings.DEFAULT_TEMPERATURE) * 0.02
    
    # Calculate new temperature
    delta_time = current_time - last_update_time if last_update_time > 0 else settings.TEMPERATURE_UPDATE_INTERVAL
    delta_time = min(delta_time, 1.0)  # Cap to avoid huge jumps
    
    current_temperature += (heat_effect - cooling_factor) * 0.1 * delta_time + random_factor
    
    # Enforce reasonable limits
    current_temperature = max(settings.DEFAULT_TEMPERATURE, current_temperature)
    current_temperature = min(550, current_temperature)  # Max reasonable coffee roasting temp
    
    last_update_time = current_time
    
    logger.debug(f"Simulated temperature: {current_temperature:.2f}°F, Heat: {heat_level}")
    return current_temperature

def simulate_first_crack(current_temp: float) -> bool:
    """
    Determine if the first crack would happen at this temperature.
    
    Args:
        current_temp: Current temperature in Fahrenheit
    
    Returns:
        bool: True if first crack temperature range
    """
    # First crack usually occurs between 365-385°F
    return 365 <= current_temp <= 385

def simulate_second_crack(current_temp: float) -> bool:
    """
    Determine if the second crack would happen at this temperature.
    
    Args:
        current_temp: Current temperature in Fahrenheit
    
    Returns:
        bool: True if second crack temperature range
    """
    # Second crack usually occurs between 435-450°F
    return 435 <= current_temp <= 450

def get_roast_stage(current_temp: float) -> str:
    """
    Determine the current roast stage based on temperature.
    
    Args:
        current_temp: Current temperature in Fahrenheit
    
    Returns:
        str: Description of roast stage
    """
    if current_temp < 200:
        return 'Green'
    elif current_temp < 300:
        return 'Yellow'
    elif current_temp < 350:
        return 'Light Brown'
    elif current_temp < 400:
        return 'Medium Brown'
    elif current_temp < 435:
        return 'Dark Brown'
    else:
        return 'Nearly Black'